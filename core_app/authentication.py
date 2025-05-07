from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from rest_framework.authentication import SessionAuthentication
from django.db.models import Q

CustomUser = get_user_model()

class EmailBackend(ModelBackend):
    # rewrite BackEnd for authenticating user base on Email
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = CustomUser.objects.get(email__iexact=email)
            if user.check_password(password):
                return user
        except CustomUser.DoesNotExist:
            return None

class PhoneBackend(ModelBackend):
    # rewrite BackEnd for authenticating user base on phone number and otp
    def authenticate(self, request, phone=None, password=None, **kwargs):
        try:
            user = CustomUser.objects.get(phone__iexact=phone)
            if user.check_password(password):
                return user
        except CustomUser.DoesNotExist:
            return None

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return
