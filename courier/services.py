from .models import CourierAssignment, Courier, Zone
from orders.models import Order
import random

def auto_assign_courier(order):
    """
    Auto assign courier based on order shipping address city/zone
    """
    address = order.address
    if not address:
        return None

    # Find zones in city
    zones = Zone.objects.filter(city__name=address.city)
    if not zones.exists():
        return None

    # Find active couriers in these zones
    possible_couriers = Courier.objects.filter(is_active=True, zones__in=zones).distinct()
    if not possible_couriers.exists():
        return None

    # Random pick one courier
    courier = random.choice(possible_couriers)
    assignment, created = CourierAssignment.objects.get_or_create(order=order, defaults={'courier': courier})
    return assignment
