from django.contrib import admin
from .models import Store
# Register your models here.
@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner', 'address', 'created_at')
    search_fields = ('name', 'owner__username', 'address')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)
