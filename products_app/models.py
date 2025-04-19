import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _
from store_app.models import Store
from users_app.models import CustomUser
# Create your models here.
class Category(models.Model):
    name = models.CharField(_("Category Name"), max_length=100, unique=True)
    parent = models.ForeignKey(
        'self',  # Self relation
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name=_('subcategories'),
        verbose_name=_("Parent Category")
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return ' → '.join(full_path[::-1])  # Shows full path like: Electronics → Phones → Smartphones

class Product(models.Model):
    name = models.CharField(_("Product Name"), max_length=100, unique=True,blank=False,null=False)
    store = models.ForeignKey(Store, on_delete=models.PROTECT,blank=False,null=False)
    category = models.ForeignKey(Category, on_delete=models.PROTECT,blank=False,null=False)
    brand = models.CharField(_("Brand Name"), max_length=50, blank=False,null=False)
    descrition = models.TextField(_("Description"), blank=False,null=False)
    price = models.DecimalField(_("Price"), max_digits=10, decimal_places=2)
    image = models.ImageField(_("Image"), upload_to="products/", blank=False, null=False)
    quantity = models.IntegerField(_("Quantity"), blank=False, null=False)
    is_active = models.BooleanField(_("Active"), default=True)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)


class Comment(models.Model):
    RATE_CHOICES = (
        (1, "1"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (5, "5"))
    STATUS_CHOICES = ((_("approved"), _("Approved")),(_("waiting"), _("Waiting")),(_("deny"), _("Deny")))
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='comment')
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='comments')
    rating = models.IntegerField(null=False,blank=False,choices=RATE_CHOICES)
    description = models.TextField(null=False,blank=False)
    reply_comment = models.ForeignKey('self',on_delete=models.CASCADE,related_name='child_comments',blank=True,null=True)
    status = models.CharField(_("Status"),choices=STATUS_CHOICES,blank=False,null=False,default=STATUS_CHOICES[1][0])
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    update_at = models.DateTimeField(_("Updated at"), auto_now=True)
    class Meta:
        verbose_name_plural = _("Comments")