from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order
from .services import auto_assign_courier

@receiver(post_save, sender=Order)
def assign_courier_on_order(sender, instance, created, **kwargs):
    # Only assign when order is confirmed
    if instance.status == 'confirmed':
        auto_assign_courier(instance)
