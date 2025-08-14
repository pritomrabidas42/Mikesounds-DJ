from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.db.models import F, Sum, DecimalField, ExpressionWrapper
from products.models import Product

class Supplier(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.name


class Inventory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='inventory')
    current_stock = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.title} - Stock: {self.current_stock}"


class Purchase(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchases')
    date = models.DateField(default=timezone.now)
    note = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"PO#{self.id} - {self.supplier.name} - {self.date}"

    @property
    def total_amount(self):
        agg = self.items.aggregate(
            total=Sum(
                ExpressionWrapper(
                    F('quantity') * F('price'),
                    output_field=DecimalField(max_digits=12, decimal_places=2)
                )
            )
        )
        return agg['total'] or 0


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.product.title} x {self.quantity}"

    @property
    def line_total(self):
        return self.quantity * self.price


class SupplierPayment(models.Model):
    METHOD_CHOICES = [
        ('bkash', 'bKash'),
        ('nagad', 'Nagad'),
        ('rocket', 'Rocket'),
        ('bank', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('card', 'Card'),
    ]
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='payments')
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    account_holder = models.CharField(max_length=255, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    bank_branch = models.CharField(max_length=100, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    date = models.DateField(default=timezone.now)
    note = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.supplier.name} - {self.method} - {self.amount}"


class SupplierLedger(models.Model):
    TRANSACTION_TYPES = [
        ('debit', 'Debit'),
        ('credit', 'Credit'),
    ]
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='ledger')
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    transaction_type = models.CharField(max_length=6, choices=TRANSACTION_TYPES)
    date = models.DateField(default=timezone.now)
    purchase = models.ForeignKey(Purchase, on_delete=models.SET_NULL, null=True, blank=True)
    payment = models.ForeignKey(SupplierPayment, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.supplier.name} - {self.transaction_type} - {self.amount}"
