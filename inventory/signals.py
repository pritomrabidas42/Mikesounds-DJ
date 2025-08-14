from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import PurchaseItem, Inventory, SupplierLedger, SupplierPayment


# পুরনো quantity আর product ট্র্যাক করা
@receiver(pre_save, sender=PurchaseItem)
def track_old_quantity_and_product(sender, instance, **kwargs):
    if instance.pk:
        old_item = PurchaseItem.objects.get(pk=instance.pk)
        instance._old_quantity = old_item.quantity
        instance._old_product = old_item.product
    else:
        instance._old_quantity = 0
        instance._old_product = None


# PurchaseItem তৈরি বা আপডেট হলে ইনভেন্টরি আপডেট
@receiver(post_save, sender=PurchaseItem)
def update_inventory_on_purchase(sender, instance, created, **kwargs):
    # প্রোডাক্ট পরিবর্তন হলে পুরনো প্রোডাক্ট থেকে স্টক কমানো
    if not created and instance._old_product and instance._old_product != instance.product:
        old_inventory, _ = Inventory.objects.get_or_create(product=instance._old_product)
        old_inventory.current_stock -= instance._old_quantity
        if old_inventory.current_stock < 0:
            old_inventory.current_stock = 0
        old_inventory.save()
        instance._old_quantity = 0

    # নতুন বা আপডেট quantity এর জন্য স্টক অ্যাডজাস্ট
    inventory, _ = Inventory.objects.get_or_create(product=instance.product)
    qty_diff = instance.quantity - getattr(instance, "_old_quantity", 0)
    inventory.current_stock += qty_diff
    if inventory.current_stock < 0:
        inventory.current_stock = 0
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
        if inventory.current_stock < 0:
            inventory.current_stock = 0
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
