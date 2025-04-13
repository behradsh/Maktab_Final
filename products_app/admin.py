from django.contrib import admin
from .models import Category,Product,Comment

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "created_at")
    list_filter = ("parent", "created_at")
    search_fields = ("name",)
    ordering = ("parent__name", "name")  # Orders subcategories under parents

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "store", "category", "brand", "price", "quantity")
    list_filter = ("store", "category", "brand")
    search_fields = ("name", "brand", "description")
    list_editable = ("price", "quantity")
    autocomplete_fields = ("store", "category")
    readonly_fields = ("image",)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "rating", "status", "description_preview")
    list_filter = ("status", "rating", "product")
    search_fields = ("user__username", "product__name", "description")
    autocomplete_fields = ("user", "product", "reply_comment")

    def description_preview(self, obj):
        return obj.description[:40] + "..." if len(obj.description) > 40 else obj.description

    description_preview.short_description = "Description"
