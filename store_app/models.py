from django.db import models
from django.utils.translation import gettext_lazy as _
from users_app.models import CustomUser

# Create your models here.
class Store(models.Model):
    name = models.CharField(_("Name of Store"), max_length=80,blank=False, null=False)
    address = models.CharField(_("Address of Store"), max_length=150,blank=False, null=False)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    owner = models.OneToOneField(CustomUser, verbose_name=_("Owner"), on_delete=models.PROTECT)
