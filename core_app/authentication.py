from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

CustomUser = get_user_model()

class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = CustomUser.objects.get(email__iexact=email)
            if user.check_password(password):
                return user
        except CustomUser.DoesNotExist:
            return None

class PhoneBackend(ModelBackend):
    def authenticate(self, request, phone=None, password=None, **kwargs):
        try:
            user = CustomUser.objects.get(phone__iexact=phone)
            if user.check_password(password):
                return user
        except CustomUser.DoesNotExist:
            return None