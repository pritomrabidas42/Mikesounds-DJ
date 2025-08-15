from django.db import models
from django.contrib.auth.models import User
from orders.models import Order, Address
from django.utils import timezone

class City(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Zone(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='zones')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.city.name} - {self.name}"

class Courier(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    zones = models.ManyToManyField(Zone, related_name='couriers')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class CourierAssignment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='courier_assignment')
    courier = models.ForeignKey(Courier, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"Order {self.order.id} -> {self.courier.name}"

