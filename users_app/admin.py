from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser,Address
# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'phone', 'email', 'is_staff', 'password','is_customer')
    list_filter = ('is_staff', 'is_customer', 'gender', 'groups')
    fieldsets = (
        ('Standard info', {'fields': ("username", "password", "first_name", "last_name", "phone", "email",'profile_img')}),
        ('other info', {'fields': ("is_staff", "is_active","is_customer" ,"groups", "user_permissions",)}),
    )
    search_fields = ('first_name__startswith', 'last_name__startswith', 'phone__startswith',)

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('customer', 'address_line', 'city', 'province', 'country','postal_code','is_default')
    list_filter = ('customer', 'city', 'province',)
    fieldsets = (
        ('Standard info', {'fields': ("customer", "address_line", "city", "province", "country", "postal_code",)}),
        ('other info', {'fields': ("is_default", )}),
    )
    search_fields = ('customer__startswith', 'province__startswith', 'city__startswith',)

