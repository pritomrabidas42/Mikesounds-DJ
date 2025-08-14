from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Order, OrderItem
from inventory.models import Inventory

@receiver(post_save, sender=Order)
def adjust_inventory(sender, instance, created, **kwargs):
    if created and instance.status == 'confirmed':
        for item in instance.items.all():
            inventory = Inventory.objects.get(product=item.product)
            inventory.current_stock -= item.quantity
            if inventory.current_stock < 0:
                inventory.current_stock = 0
            inventory.save()

@receiver(pre_delete, sender=Order)
def restore_inventory(sender, instance, **kwargs):
    for item in instance.items.all():
        inventory = Inventory.objects.get(product=item.product)
        inventory.current_stock += item.quantity
        inventory.save()
