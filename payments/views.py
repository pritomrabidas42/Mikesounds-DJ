from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .models import Transaction
from orders.models import Order
import hmac, hashlib, json , stripe
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

stripe.api_key = settings.STRIPE_SECRET_KEY

# Payment init
def payment_init(request, order_id, gateway):
    order = get_object_or_404(Order, id=order_id)
    if order.payment_status == 'paid':
        return render(request, 'payment/already_paid.html', {'order': order})

    txn = Transaction.objects.create(
        order=order,
        amount=order.grand_total,
        gateway=gateway,
        status='pending'
    )

    if gateway == 'stripe':
        intent = stripe.PaymentIntent.create(
            amount=int(order.grand_total*100),  # cents
            currency='usd',
            metadata={'txn_id': txn.id, 'order_id': order.id},
        )
        return render(request, 'payment/stripe_redirect.html', {'client_secret': intent.client_secret})

    elif gateway == 'sslcommerz':
        payload = {
            'store_id': settings.SSLCOMMERZ_STORE_ID,
            'store_passwd': settings.SSLCOMMERZ_STORE_PASS,
            'total_amount': str(order.grand_total),
            'currency': 'BDT',
            'tran_id': txn.id,
            'success_url': request.build_absolute_uri(f'/payment/callback/{txn.id}/'),
            'fail_url': request.build_absolute_uri(f'/payment/callback/{txn.id}/'),
        }
        return render(request, 'payment/gateway_redirect.html', {'payload': payload, 'gateway_url': settings.SSLCOMMERZ_URL})

    elif gateway == 'bkash':
        payload = {
            'merchant_msisdn': settings.BKASH_MERCHANT,
            'amount': str(order.grand_total),
            'order_id': txn.id,
            'callback_url': request.build_absolute_uri(f'/payment/callback/{txn.id}/')
        }
        return render(request, 'payment/gateway_redirect.html', {'payload': payload, 'gateway_url': settings.BKASH_URL})

    elif gateway == 'nogod':
        payload = {
            'merchant_number': settings.NOGOD_MERCHANT_NUMBER,
            'order_id': txn.id,
            'amount': str(order.grand_total),
            'callback_url': request.build_absolute_uri(f'/payment/callback/{txn.id}/')
        }
        return render(request, 'payment/gateway_redirect.html', {'payload': payload, 'gateway_url': settings.NOGOD_URL})

# Callback handler
@csrf_exempt
def payment_callback(request, txn_id):
    txn = get_object_or_404(Transaction, id=txn_id)
    order = txn.order

    # Gateway specific signature validation
    if txn.gateway == 'stripe':
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except:
            txn.status = 'failed'
            txn.save()
            return render(request, 'payment/failed.html', {'txn': txn})
        if event['type'] == 'payment_intent.succeeded':
            txn.status = 'success'
            txn.raw_response = event
            txn.verified_at = timezone.now()
            txn.save()

    else:
        data = request.POST.dict()
        signature = data.pop('signature', '')
        secret = {
            'bkash': settings.BKASH_SECRET,
            'nogod': settings.NOGOD_SECRET,
            'sslcommerz': settings.SSLCOMMERZ_SECRET
        }.get(txn.gateway, '')
        if secret:
            calculated = hmac.new(secret.encode(), "&".join(f"{k}={v}" for k,v in sorted(data.items())).encode(), hashlib.sha256).hexdigest()
            if calculated != signature or float(data.get('amount',0)) < float(txn.amount):
                txn.status = 'failed'
                txn.save()
                return render(request, 'payment/failed.html', {'txn': txn})
            txn.status = 'success'
            txn.raw_response = data
            txn.verified_at = timezone.now()
            txn.save()

    if txn.status == 'success':
        order.payment_status = 'paid'
        order.status = 'confirmed'
        order.save()
        from inventory.services import decrement_stock_for_order
        decrement_stock_for_order(order)
        return render(request, 'payment/success.html', {'txn': txn})
    return render(request, 'payment/failed.html', {'txn': txn})
