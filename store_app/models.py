from django.db import models
from django.utils.translation import gettext_lazy as _
from users_app.models import CustomUser

# Create your models here.
class Store(models.Model):
    name = models.CharField(_("Name of Store"), max_length=80,blank=False, null=False)
    address = models.CharField(_("Address of Store"), max_length=150,blank=False, null=False)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    owner = models.OneToOneField(CustomUser, verbose_name=_("Owner"), on_delete=models.PROTECT)
    logo = models.ImageField(_("Logo of Store"),upload_to='store_logo', null=True, blank=True)
    is_active = models.BooleanField(_("Active"), default=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)
    class Meta:
        verbose_name = _("Store")
        verbose_name_plural = _("Stores")
        ordering = ['-created_at']
    def __str__(self):
        return self.name