from django.utils.crypto import get_random_string
from django.utils import timezone
from django.urls import reverse

from rest_framework import serializers

from .models import CustomUser
from .tasks import send_verification_email_task


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'email',
            'password',
            'role',
            'bio'
        ]

        extra_kwargs = {
            "password": {
                "write_only": True
            }
        }

    def create(self, validated_data):

        user = CustomUser(**validated_data)

        user.set_password(validated_data['password'])

        user.verification_token = get_random_string(length=32)

        user.save()

        verification_link = self.context['request'].build_absolute_uri(
            reverse(
                viewname='verify_email',
                kwargs={
                    'token': user.verification_token
                }
            )
        )

        send_verification_email_task.delay(
            user.id,
            verification_link
        )

        return user


class UserLoginSerializer(serializers.Serializer):

    email = serializers.EmailField()
    password = serializers.CharField()


class UserUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = [
            "bio"
        ]

    def update(self, instance, validated_data):

        instance.bio = validated_data.get(
            'bio',
            instance.bio
        )

        instance.save()

        return instance


class ForgotPasswordSerializer(serializers.Serializer):

    email = serializers.EmailField()

    def validate_email(self, value):

        try:
            user = CustomUser.objects.get(
                email=value
            )

        except CustomUser.DoesNotExist:
            raise serializers.ValidationError(
                "No user found with this email."
            )

        reset_token = get_random_string(
            length=64
        )

        user.password_reset_token = reset_token

        user.password_reset_token_created_at = timezone.now()

        user.save(
            update_fields=[
                'password_reset_token',
                'password_reset_token_created_at'
            ]
        )

        self.user = user

        return value


class ResetPasswordSerializer(serializers.Serializer):

    token = serializers.CharField()

    new_password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    def validate(self, attrs):

        token = attrs.get('token')

        try:
            user = CustomUser.objects.get(
                password_reset_token=token
            )

        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({
                "token": "Invalid or expired reset token."
            })

        if not user.password_reset_token_created_at:
            raise serializers.ValidationError({
                "token": "Invalid or expired reset token."
            })

        token_age = (
            timezone.now()
            - user.password_reset_token_created_at
        )

        if token_age.total_seconds() > 3600:
            raise serializers.ValidationError({
                "token": "Password reset token has expired."
            })

        attrs['user'] = user

        return attrs

    def save(self):

        user = self.validated_data['user']

        new_password = self.validated_data['new_password']

        user.set_password(new_password)

        user.password_reset_token = None

        user.password_reset_token_created_at = None

        user.save(
            update_fields=[
                'password',
                'password_reset_token',
                'password_reset_token_created_at'
            ]
        )

        return user