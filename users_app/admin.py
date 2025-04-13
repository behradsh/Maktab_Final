from django.contrib import admin
from .models import CustomUser
# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'phone', 'email', 'is_staff', 'password')
    list_filter = ('is_staff',)
    fields = [
        ("username", "password", "first_name", "last_name", "phone", "email",),
        ("is_staff", "is_active", "groups", "user_permissions"),
    ]
    search_fields = ('first_name__startswith', 'last_name__startswith', 'phone__startswith',)