from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'phone', 'email', 'is_staff', 'password','is_customer')
    list_filter = ('is_staff', 'is_customer', 'gender', 'groups')
    fieldsets = (
        ('Standard info', {'fields': ("username", "password", "first_name", "last_name", "phone", "email",)}),
        ('other info', {'fields': ("is_staff", "is_active", "groups", "user_permissions",)}),
    )
    search_fields = ('first_name__startswith', 'last_name__startswith', 'phone__startswith',)