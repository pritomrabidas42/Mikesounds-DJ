from celery import shared_task
from .models import Transaction
from django.utils import timezone

@shared_task
def clean_abandoned_payments():
    transactions = Transaction.objects.filter(status='pending', created_at__lt=timezone.now()-timezone.timedelta(hours=1))
    for txn in transactions:
        txn.status = 'failed'
        txn.save()
