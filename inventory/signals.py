from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import PurchaseItem, Inventory, SupplierLedger, SupplierPayment

# পুরনো quantity ট্র্যাক করা
@receiver(pre_save, sender=PurchaseItem)
def track_old_quantity(sender, instance, **kwargs):
    if instance.pk:
        old_item = PurchaseItem.objects.get(pk=instance.pk)
        instance._old_quantity = old_item.quantity
    else:
        instance._old_quantity = 0

# PurchaseItem তৈরি বা আপডেট হলে ইনভেন্টরি আপডেট
@receiver(post_save, sender=PurchaseItem)
def update_inventory_on_purchase(sender, instance, created, **kwargs):
    inventory, _ = Inventory.objects.get_or_create(product=instance.product)
    qty_diff = instance.quantity - getattr(instance, "_old_quantity", 0)
    inventory.current_stock += qty_diff
    inventory.save()

    # শুধু নতুন হলে লেজার ডেবিট
    if created:
        if not SupplierLedger.objects.filter(
            supplier=instance.purchase.supplier,
            amount=instance.line_total,
            transaction_type='debit',
            purchase=instance.purchase
        ).exists():
            SupplierLedger.objects.create(
                supplier=instance.purchase.supplier,
                amount=instance.line_total,
                transaction_type='debit',
                purchase=instance.purchase
            )

# PurchaseItem ডিলিট হলে ইনভেন্টরি কমানো
@receiver(post_delete, sender=PurchaseItem)
def update_inventory_on_delete(sender, instance, **kwargs):
    inventory = Inventory.objects.filter(product=instance.product).first()
    if inventory:
        inventory.current_stock -= instance.quantity
        inventory.save()

# SupplierPayment তৈরি হলে লেজার ক্রেডিট
@receiver(post_save, sender=SupplierPayment)
def update_ledger_on_payment(sender, instance, created, **kwargs):
    if created:
        if not SupplierLedger.objects.filter(
            supplier=instance.supplier,
            amount=instance.amount,
            transaction_type='credit',
            payment=instance
        ).exists():
            SupplierLedger.objects.create(
                supplier=instance.supplier,
                amount=instance.amount,
                transaction_type='credit',
                payment=instance
            )
