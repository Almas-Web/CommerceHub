from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
@shared_task
def send_verification_email_task(user_id, verification_link):
    from .models import CustomUser
    user = CustomUser.objects.get(id=user_id)

    subject = 'Verify your CommerceHub email'

    html_content = render_to_string(
        'emails/verification_email.html',
        {
            'user': user,
            'verification_link': verification_link
        }
    )

    email = EmailMultiAlternatives(
        subject,
        'Please verify your CommerceHub account.',
        'noreply@commercehub.com',
        [user.email]
    )

    email.attach_alternative(
        html_content,
        'text/html'
    )

    email.send(fail_silently=False)

    return f'Verification email sent to {user.email}'


@shared_task
def send_password_reset_email_task(user_id, reset_link):
    from .models import CustomUser

    user = CustomUser.objects.get(id=user_id)

    subject = 'Reset your CommerceHub password'

    html_content = render_to_string(
        'emails/password_reset_email.html',
        {
            'user': user,
            'reset_link': reset_link
        }
    )

    email = EmailMultiAlternatives(
        subject,
        'Click the link to reset your CommerceHub password.',
        'noreply@commercehub.com',
        [user.email]
    )

    email.attach_alternative(
        html_content,
        'text/html'
    )

    email.send(fail_silently=False)

    return f'Password reset email sent to {user.email}'