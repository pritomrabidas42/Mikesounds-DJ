from django.db import models
from django.contrib.auth.models import User
from products.models import Product, ProductVariation, ProductImage
from inventory.models import Inventory
from django.utils import timezone

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation = models.ForeignKey(ProductVariation, null=True, blank=True, on_delete=models.SET_NULL)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def line_total(self):
        return self.quantity * self.unit_price

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses',default=None, null=True)
    full_name = models.CharField(max_length=255,default="Jon Doe")
    phone = models.CharField(max_length=20,default="1234567890")
    line1 = models.CharField(max_length=255,default="123 Main St")
    line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100,default="Anytown")
    state = models.CharField(max_length=100,default="CA")
    postal_code = models.CharField(max_length=20,default="12345")
    country = models.CharField(max_length=50,default="USA")
    is_billing = models.BooleanField(default=False)
    is_shipping = models.BooleanField(default=False)
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending','Pending'),
        ('confirmed','Confirmed'),
        ('packed','Packed'),
        ('shipped','Shipped'),
        ('delivered','Delivered'),
        ('canceled','Canceled')
    ]
    PAYMENT_STATUS = [
        ('pending','Pending'),
        ('partial','Partial'),
        ('paid','Paid')
    ]
    address = models.ForeignKey(Address, null=True, blank=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation = models.ForeignKey(ProductVariation, null=True, blank=True, on_delete=models.SET_NULL)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def line_total(self):
        return self.quantity * self.unit_price

class OrderAssignment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    staff = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_staff': True})
    assigned_at = models.DateTimeField(auto_now_add=True)
    auto_assigned = models.BooleanField(default=True)
    remarks = models.TextField(default="")

class ShipmentTracking(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tracking')
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    updated_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True)


