from django.db import models
from django.utils.translation import gettext_lazy as _
from users_app.models import CustomUser,Address
from django.core.validators import MinValueValidator,MaxValueValidator
from products_app.models import Product
from store_app.models import Store
# Create your models here.
ORDER_STATUS_CHOICES = (
    (_("pending"), _("Pending")),
    (_("processing"), _("Processing")),
    (_("shipped"), _("Shipped")),
    (_("delivered"), _("Delivered")),
    (_("cancelled"), _("Cancelled")),
)
class Orders(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.PROTECT,blank=False)
    address = models.ForeignKey(Address, on_delete=models.PROTECT,blank=False,null=True)
    status = models.CharField(_("Status"), choices=ORDER_STATUS_CHOICES, default="pending")
    discount = models.IntegerField(_("Discount")
                                   ,validators=[MinValueValidator(0),MaxValueValidator(100)]
                                   ,help_text=_("The discount applied to the order"),null=True,blank=True)
    total_amount = models.DecimalField(_("Total Amount"), max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)
    store = models.ForeignKey(Store, on_delete=models.PROTECT, related_name='orders',null=True,blank=True)

    class Meta:
        verbose_name_plural = _("Orders")
    def __str__(self):
        return f"Order #{self.pk} by {self.customer.username}"
    # def save(self,*args,**kwargs):
    #     if not self.discount:
    #         self.discount=0
    #     Items = OrderItems.objects.filter(order=self)
    #     sum_total = 0
    #     for item in Items:
    #         if item.discount:
    #             sum_total += item.price * item.quantity * (1/item.discount)
    #         sum_total += item.price * item.quantity
    #     self.total_amount += sum_total
    #     super().save(*args, **kwargs)

class OrderItemsManager(models.Manager):
    def create(self, **kwargs):
        if 'product' in kwargs and ('price' not in kwargs or kwargs['price'] == 0):
            kwargs['price'] = kwargs['product'].price
        return super().create(**kwargs)


class OrderItems(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.PROTECT,blank=True,null=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT,blank=True,null=True)
    quantity = models.PositiveIntegerField(_("Quantity"),blank=False,null=False)
    price = models.DecimalField(_("Price"), max_digits=10, decimal_places=2,null=True,blank=True)
    discount = models.PositiveIntegerField(_("Discount"),
                                   validators=[MinValueValidator(0),MaxValueValidator(100)],
                                   help_text=_("The discount applied to the order"),null=True,blank=True)
    objects = OrderItemsManager()

    def save(self, *args, **kwargs):
        # If no price is set and product exists, use the product's price
        if self.product and (not self.price or self.price == 0):
            if not self.discount:
                self.discount=0
            if self.discount == 0:
                self.price = self.product.price * self.quantity
            else:
                calculate_discount = ((float(self.product.price) * float(self.quantity))*float(self.discount))/100
                self.price = (float(self.product.price) * float(self.quantity)) - calculate_discount
            self.product.quantity -= self.quantity
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = _("Order Items")

