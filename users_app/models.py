from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from rest_framework_simplejwt.tokens import RefreshToken
from config import settings

PHONE_VALIDATOR = RegexValidator(
    regex=r'^(\+98|0)?9\d{9}$',
    message="Phone number must be entered in the format: '+989123456789' or '09123456789'."
)
PROVINCE_CHOICES = [
    (_('tehran'), _('Tehran')),
    (_('qom'), _('Qom')),
    (_('markazi'), _('Markazi')),
    (_('qazvin'), _('Qazvin')),
    (_('gilan'), _('Gilan')),
    (_('ardabil'), _('Ardabil')),
    (_('zanjan'), _('Zanjan')),
    (_('east_azarbaijan'), _('East Azarbaijan')),
    (_('west_azarbaijan'), _('West Azarbaijan')),
    (_('kurdistan'), _('Kurdistan')),
    (_('hamadan'), _('Hamadan')),
    (_('kermanshah'), _('Kermanshah')),
    (_('ilam'), _('Ilam')),
    (_('lorestan'), _('Lorestan')),
    (_('khuzestan'), _('Khuzestan')),
    (_('chahar_mahaal_and_bakhtiari'), _('Chahar Mahaal and Bakhtiari')),
    (_('kohkiluyeh_and_buyer_ahmad'), _('Kohkiluyeh and Buyer Ahmad')),
    (_('bushehr'), _('Bushehr')),
    (_('fars'), _('Fars')),
    (_('hormozgan'), _('Hormozgan')),
    (_('sistan_and_baluchistan'), _('Sistan and Baluchistan')),
    (_('kerman'), _('Kerman')),
    (_('yazd'), _('Yazd')),
    (_('esfahan'), _('Esfahan')),
    (_('semnan'), _('Semnan')),
    (_('mazandaran'), _('Mazandaran')),
    (_('golestan'), _('Golestan')),
    (_('north_khorasan'), _('North Khorasan')),
    (_('razavi_khorasan'), _('Razavi Khorasan')),
    (_('south_khorasan'), _('South Khorasan')),
    (_('alborz'), _('Alborz')),
]


# Create your models here.
class CustomUser(AbstractUser):
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_customer = models.BooleanField(_("customer status"),
                                      help_text=_("Designates whether the user is buyer or seller."),
                                      blank=False, null=False)
    gender = models.BooleanField(_("gender status"),
                                 default=False,
                                 help_text=_("Designates whether the user is man(1) or woman(0)."),
                                 blank=False, null=False)
    phone = models.CharField(_("Phone number"), max_length=13, blank=False, null=False, unique=True,
                             validators=[PHONE_VALIDATOR])
    email = models.EmailField(_("email address"), blank=False, null=False, unique=True)
    profile_img = models.ImageField(_("profile image"), upload_to='profile_pics', blank=True, null=True, )
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
    customer = models.ForeignKey(CustomUser, blank=False, null=False, on_delete=models.PROTECT)
    address_line = models.TextField(_("Address line"), max_length=100, blank=False, null=False)
    city = models.CharField(_("City"), max_length=30, blank=False, null=False)
    province = models.CharField(_("Province"), max_length=30, blank=False,choices=PROVINCE_CHOICES,default=PROVINCE_CHOICES[0][0])
    country = models.CharField(_("Country"), max_length=30, blank=False, null=False, default=_("Iran"))
    postal_code = models.CharField(_("Postal code"), max_length=10, blank=False, null=False)
    is_default = models.BooleanField(_("is default"), default=False)

    def __str__(self):
        return f"{self.customer}, {self.city}, {self.country}"

    class Meta:
        verbose_name_plural = 'Address'
