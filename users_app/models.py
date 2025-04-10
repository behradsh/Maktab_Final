from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _
# Create your models here.
# class User(AbstractUser):
#     password = models.CharField(max_length=32,blank=False,null=False)
#     fa_firstname = models.CharField(_("first name"), max_length=30, blank=True)
#     fa_last_name = models.CharField(_("last name"), max_length=30, blank=True)
#     is_staff = models.BooleanField(
#         _("staff status"),
#         default=False,
#         help_text=_("Designates whether the user can log into this admin site."),
#     )
#     is_customer = models.BooleanField(_("customer status"),
#                                       default=False,
#                                       help_text=_("Designates whether the user is buyer or seller."),)
#     gender = models.BooleanField(_("gender status"),
#                                       default=False,
#                                       help_text=_("Designates whether the user is man(1) or woman(0)."), )
#     phone = PhoneNumberField(_("phone number"), blank=False, null=False)
#     email = models.EmailField(_("email address"), blank=False, null=False)

    def __str__(self):
        return f"{self.username} - {self.email}"