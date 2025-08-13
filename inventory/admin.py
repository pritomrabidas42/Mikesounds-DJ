from django.contrib import admin
from .models import *

class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'date', 'total_amount')
    inlines = [PurchaseItemInline]

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email')

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'current_stock', 'last_updated')

@admin.register(SupplierPayment)
class SupplierPaymentAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'method', 'amount', 'date')

@admin.register(SupplierLedger)
class SupplierLedgerAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'transaction_type', 'amount', 'date')
    list_filter = ('transaction_type', 'date')

