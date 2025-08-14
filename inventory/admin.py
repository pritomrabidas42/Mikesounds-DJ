from django.contrib import admin
from .models import Purchase, PurchaseItem, Supplier, Inventory, SupplierPayment, SupplierLedger


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1
    autocomplete_fields = ['product']  # দ্রুত প্রোডাক্ট সার্চ


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplier', 'date', 'total_amount')
    list_filter = ('date', 'supplier')
    search_fields = ('supplier__name',)
    inlines = [PurchaseItemInline]


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email')
    search_fields = ('name', 'phone', 'email')


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'current_stock', 'last_updated')
    search_fields = ('product__title',)
    autocomplete_fields = ['product']


@admin.register(SupplierPayment)
class SupplierPaymentAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'method', 'amount', 'date')
    list_filter = ('method', 'date')
    search_fields = ('supplier__name', 'transaction_id')


@admin.register(SupplierLedger)
class SupplierLedgerAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'transaction_type', 'amount', 'date')
    list_filter = ('transaction_type', 'date')
    search_fields = ('supplier__name',)
