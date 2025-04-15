from celery import shared_task
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .models import CustomUser
import logging
from config import settings
from django.core.mail import send_mail


logger = logging.getLogger(__name__)



@shared_task
def send_otp_email(email, verification_code):
    try:
        print(f"Attempting to send email to {email} using host {settings.EMAIL_HOST}")
        send_mail(
            'Verification Code',
            f'Your verification code is: {verification_code}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        print(f"Email sent successfully to {email}")
        return True
    except Exception as e:
        print(f"Failed to send email to {email}: {str(e)}")
        return False


@shared_task
def clear_expired_otp_codes():
    """
    Clear expired OTP codes from UserProfile models
    This function runs as a scheduled Celery task
    """
    try:
        with transaction.atomic():
            # Get profiles with non-null OTP and expired time
            expired_profiles = CustomUser.objects.filter(
                otp__isnull=False,
                otp_expiry_time__lt=timezone.now()
            )

            # Log the number of profiles to clear
            count = expired_profiles.count()

            # Reset OTP fields
            expired_profiles.update(
                otp=None,
                otp_expiry_time=None
            )

            logger.info(f"Successfully cleared {count} expired OTP codes")
            return f"Cleared {count} expired OTP codes"

    except Exception as e:
        logger.error(f"Error clearing expired OTP codes: {str(e)}")
        # Re-raise the exception for Celery's retry mechanism
        raise
