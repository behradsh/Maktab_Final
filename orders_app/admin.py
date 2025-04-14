from django.contrib import admin
from .models import Orders,OrderItems
# Register your models here.

@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'status', 'discount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__username', 'customer__email', 'id')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('customer', 'address', 'status')
        }),
        ('Pricing', {
            'fields': ('total_amount', 'discount')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    # Add ability to update order status in bulk
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']

    def mark_as_processing(self, request, queryset):
        queryset.update(status='processing')

    mark_as_processing.short_description = "Mark selected orders as processing"

    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')

    mark_as_shipped.short_description = "Mark selected orders as shipped"

    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')

    mark_as_delivered.short_description = "Mark selected orders as delivered"

    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')

    mark_as_cancelled.short_description = "Mark selected orders as cancelled"


@admin.register(OrderItems)
class OrderItemsAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price', 'discount')
    list_filter = ('order__status',)
    search_fields = ('order__id', 'product__name')
    raw_id_fields = ('order', 'product')  # Useful if you have many orders/products
    readonly_fields = ('price', 'discount')
