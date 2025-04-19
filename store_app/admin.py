from django.contrib import admin
from .models import Store,StoreEmployee
# Register your models here.
@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner', 'address', 'created_at','city')
    search_fields = ('name', 'owner__username','owner__email','address')
    list_filter = ('created_at','is_active')
    readonly_fields = ('created_at',)

@admin.register(StoreEmployee)
class StoreEmployeeAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'store_id','is_manager','is_operator')
    list_filter = ('user_id', 'store_id','is_manager','is_operator')
    fieldsets = (
        ('Standard info', {'fields': ("user_id", "store_id",'is_manager','is_operator')}),
    )
    search_fields = ('role__startswith', 'user_id__startswith')