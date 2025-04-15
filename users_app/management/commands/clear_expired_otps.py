from django.core.management.base import BaseCommand
from src.config.users_app.tasks import clear_expired_otp_codes


class Command(BaseCommand):
    help = 'Clear expired OTP codes manually'

    def handle(self, *args, **options):
        self.stdout.write("Starting task to clear expired OTP codes...")
        result = clear_expired_otp_codes.delay()  # Run as Celery task
        self.stdout.write(self.style.SUCCESS(f"Task started with ID: {result.id}"))

        # If you want to wait for the result
        self.stdout.write("Waiting for task to complete...")
        task_result = result.get(timeout=30)  # Wait up to 30 seconds
        self.stdout.write(self.style.SUCCESS(f"Task result: {task_result}"))
