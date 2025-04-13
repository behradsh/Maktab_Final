from django.db import models
from django.utils.translation import gettext_lazy as _
from users_app.models import CustomUser,Address
from django.core.validators import MinValueValidator,MaxValueValidator
from products_app.models import Product
# Create your models here.
ORDER_STATUS_CHOICES = (
    (_("active"), _("active")),
    (_("pending"), _("pending")),
    (_("rejected"), _("rejected")),
    (_("ontheway"), _("ontheway")),
)
class Orders(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.PROTECT,blank=True,null=True)
    address = models.OneToOneField(Address, on_delete=models.PROTECT,blank=True,null=True)
    status = models.CharField(_("Status"), choices=ORDER_STATUS_CHOICES, default="pending")
    final_price = models.DecimalField(_("Final Price"), max_digits=10, decimal_places=2)
    discount = models.IntegerField(_("Discount")
                                   ,validators=[MinValueValidator(0),MaxValueValidator(100)]
                                   ,help_text=_("The discount applied to the order"),)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    class Meta:
        verbose_name_plural = _("Orders")

class OrderItems(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.PROTECT,blank=True,null=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT,blank=True,null=True)
    quantity = models.SmallIntegerField(_("Quantity"),blank=False,null=False)
    price = models.DecimalField(_("Price"), max_digits=10, decimal_places=2)
    discount = models.IntegerField(_("Discount"),
                                   validators=[MinValueValidator(0),MaxValueValidator(100)],
                                   help_text=_("The discount applied to the order"))
    class Meta:
        verbose_name_plural = _("Order Items")