from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import *
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    max_num = 3  

    def get_max_num(self, request, obj=None, **kwargs):
        return 3

class ProductVariationInline(admin.TabularInline):
    model = ProductVariation
    extra = 0

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'brand', 'status', 'created_at')
    list_filter = ('category', 'brand', 'status')
    search_fields = ('title', 'brand__name')
    inlines = [ProductImageInline, ProductVariationInline]
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)

