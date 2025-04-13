from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

PHONE_VALIDATOR = RegexValidator(
    regex=r'^(\+98|0)?9\d{9}$',
    message="Phone number must be entered in the format: '+989123456789' or '09123456789'."
)

# Create your models here.
class CustomUser(AbstractUser):
    password = models.CharField(max_length=120,blank=False,null=False)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_customer = models.BooleanField(_("customer status"),
                                      default=True,
                                      help_text=_("Designates whether the user is buyer or seller."),
                                      blank=False,null=False)
    gender = models.BooleanField(_("gender status"),
                                      default=False,
                                      help_text=_("Designates whether the user is man(1) or woman(0)."),
                                 blank=False,null=False )
    phone = models.CharField(_("Phone number"),max_length=13,blank=False,null=False,unique=True)
    email = models.EmailField(_("email address"), blank=False, null=False,validators=[PHONE_VALIDATOR])

    def __str__(self):
        return f"{self.username} - {self.email}"

class Address(models.Model):
    customer = models.ForeignKey(CustomUser,blank=False,null=False,on_delete=models.PROTECT)
    address_line = models.TextField(_("Address line"),max_length=100,blank=False,null=False)
    city = models.CharField(_("City"),max_length=30,blank=False,null=False)
    postal_code = models.CharField(_("Postal code"),max_length=10,blank=False,null=False)
    is_default = models.BooleanField(_("is default"),default=False)
