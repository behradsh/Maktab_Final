from django.contrib import admin
from .models import Orders,OrderItems
# Register your models here.

@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'status', 'final_price', 'discount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__username', 'customer__email', 'id')
    readonly_fields = ('created_at', 'final_price')
    fieldsets = (
        (None, {
            'fields': ('customer', 'address', 'status')
        }),
        ('Pricing', {
            'fields': ('final_price', 'discount')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(OrderItems)
class OrderItemsAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price', 'discount')
    list_filter = ('order__status',)
    search_fields = ('order__id', 'product__name')
    raw_id_fields = ('order', 'product')  # Useful if you have many orders/products
    readonly_fields = ('price', 'discount')