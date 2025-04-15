from django.db import models
from django.contrib.auth.models import AbstractUser,Group,Permission
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from rest_framework_simplejwt.tokens import RefreshToken
from config import settings

PHONE_VALIDATOR = RegexValidator(
    regex=r'^(\+98|0)?9\d{9}$',
    message="Phone number must be entered in the format: '+989123456789' or '09123456789'."
)

# Create your models here.
class CustomUser(AbstractUser):
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_customer = models.BooleanField(_("customer status"),
                                      help_text=_("Designates whether the user is buyer or seller."),
                                      blank=False,null=False)
    gender = models.BooleanField(_("gender status"),
                                      default=False,
                                      help_text=_("Designates whether the user is man(1) or woman(0)."),
                                 blank=False,null=False )
    phone = models.CharField(_("Phone number"),max_length=13,blank=False,null=False,unique=True,validators=[PHONE_VALIDATOR])
    email = models.EmailField(_("email address"), blank=False, null=False,unique=True)
    profile_img = models.ImageField(_("profile image"),upload_to='profile_pics',blank=True,null=True,)
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    otp = models.CharField(
        _("OTP"),
        max_length=6,
        blank=True,
        null=True,
    )
    otp_expiry_time = models.DateTimeField(
        _("OTP Expiry"),
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.username} - {self.email}"
    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    class Meta:
        permissions = ()

class Address(models.Model):
    customer = models.ForeignKey(CustomUser,blank=False,null=False,on_delete=models.PROTECT)
    address_line = models.TextField(_("Address line"),max_length=100,blank=False,null=False)
    city = models.CharField(_("City"),max_length=30,blank=False,null=False)
    postal_code = models.CharField(_("Postal code"),max_length=10,blank=False,null=False)
    is_default = models.BooleanField(_("is default"),default=False)