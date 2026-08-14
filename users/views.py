from django.shortcuts import render
from rest_framework import generics, status
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    ResetPasswordSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserUpdateSerializer,
    ForgotPasswordSerializer
)

from .models import CustomUser

from rest_framework.response import Response
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.urls import reverse
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from drf_spectacular.utils import extend_schema


# User Signup

@extend_schema(
    tags=['Authentication & Users'],
    summary='Register a new user',
    description='Create a new CommerceHub customer or seller account.'
)
class UserSignUp(generics.CreateAPIView):
    serializer_class = UserSerializer


# Verify Email

@extend_schema(
    tags=['Authentication & Users'],
    summary='Verify email address',
    description='Verify a user account using the email verification token.'
)
class VerifyEmail(generics.GenericAPIView):
    swagger_fake_view = True

    def get(self, request, token):
        user = CustomUser.objects.filter(
            verification_token=token
        ).first()

        if user:
            if user.is_verified:
                return Response({
                    "details": "Email already verified!",
                }, status=status.HTTP_400_BAD_REQUEST)

            user.is_verified = True
            user.verification_token = None
            user.save()

            return Response({
                "details": "Successfully verified!",
            }, status=status.HTTP_200_OK)

        return Response({
            "details": "Invalid token",
        }, status=status.HTTP_400_BAD_REQUEST)


# Resend Verification Email

@extend_schema(
    tags=['Authentication & Users'],
    summary='Resend verification email',
    description='Send a new email verification link to an unverified user.'
)
class ResendVerificationEmail(generics.GenericAPIView):
    swagger_fake_view = True

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')

        if not email:
            return Response({
                "details": "Email is required!",
            }, status=status.HTTP_400_BAD_REQUEST)

        user = CustomUser.objects.filter(email=email).first()

        if not user:
            return Response({
                "details": "User with this email doesn't exist!",
            }, status=status.HTTP_404_NOT_FOUND)

        if user.is_verified:
            return Response({
                "details": "Email already verified!",
            }, status=status.HTTP_400_BAD_REQUEST)

        user.verification_token = get_random_string(length=32)
        user.save()

        verification_link = request.build_absolute_uri(
            reverse(
                viewname='verify_email',
                kwargs={
                    'token': user.verification_token
                }
            ),
        )

        subject = 'Verify your CommerceHub email'

        html_content = render_to_string(
            'emails/verification_email.html',
            {
                "user": user,
                "verification_link": verification_link
            }
        )

        email_message = EmailMultiAlternatives(
            subject,
            "Please verify your CommerceHub account.",
            "noreply@commercehub.com",
            [user.email]
        )

        email_message.attach_alternative(
            html_content,
            "text/html"
        )

        email_message.send(fail_silently=False)

        return Response({
            "details": "Verification email sent!",
        }, status=status.HTTP_200_OK)


# User Login

@extend_schema(
    tags=['Authentication & Users'],
    summary='User login',
    description='Authenticate a verified user and return JWT access and refresh tokens.'
)
class UserLogin(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = CustomUser.objects.filter(email=email).first()

        if user:
            matched_password = user.check_password(password)

            if matched_password:
                if not user.is_verified:
                    return Response({
                        "details": "Email is not verified yet!",
                    }, status=status.HTTP_401_UNAUTHORIZED)

                refresh = RefreshToken.for_user(user)

                return Response({
                    "refresh_token": str(refresh),
                    "access_token": str(refresh.access_token)
                })

        return Response({
            "details": "Invalid credentials",
        }, status=status.HTTP_401_UNAUTHORIZED)


# User Profile

@extend_schema(
    tags=['Authentication & Users'],
    summary='Get or update user profile',
    description='Retrieve the authenticated user profile or update profile information.'
)
class RetrieveUpdateProfile(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer

        return UserSerializer


# Forgot Password

@extend_schema(
    tags=['Authentication & Users'],
    summary='Request password reset',
    description='Send a password reset email to the user.'
)
class ForgotPasswordView(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer

    def post(self, request):
        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        user = serializer.user

        reset_token = user.password_reset_token

        reset_link = request.build_absolute_uri(
            reverse(
                'reset_password',
                kwargs={
                    'token': reset_token
                }
            )
        )

        subject = 'Reset your CommerceHub password'

        html_content = render_to_string(
            'emails/password_reset_email.html',
            {
                'user': user,
                'reset_link': reset_link
            }
        )

        email_message = EmailMultiAlternatives(
            subject,
            'Click the link to reset your CommerceHub password.',
            'noreply@commercehub.com',
            [user.email]
        )

        email_message.attach_alternative(
            html_content,
            'text/html'
        )

        email_message.send(fail_silently=False)

        return Response({
            'details': 'Password reset email sent successfully.'
        }, status=status.HTTP_200_OK)


# Reset Password

@extend_schema(
    tags=['Authentication & Users'],
    summary='Reset password',
    description='Reset the user password using a valid password reset token.'
)
class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data={
                'token': kwargs.get('token'),
                'new_password': request.data.get('new_password')
            }
        )

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response({
            'details': 'Password reset successfully.'
        }, status=status.HTTP_200_OK)