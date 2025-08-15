from inventory.models import Inventory
from django.db import transaction

def decrement_stock_for_order(order):
    for item in order.items.select_for_update():
        inv = Inventory.objects.get(product=item.product)
        inv.current_stock -= item.quantity
        if inv.current_stock < 0:
            inv.current_stock = 0
        inv.save()

def restock_order(order):
    for item in order.items.all():
        inv = Inventory.objects.get(product=item.product)
        inv.current_stock += item.quantity
        inv.save()
