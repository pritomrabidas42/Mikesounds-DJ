from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem, Order, OrderItem, Address
from products.models import Product, ProductVariation
from inventory.models import Inventory
from django.db import transaction

@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product', 'variation').prefetch_related('product__images')
    return render(request, 'orders/cart.html', {'cart': cart, 'items': items})

@login_required
def add_to_cart(request, product_id, variation_id=None):
    product = get_object_or_404(Product, id=product_id)
    variation = None
    if request.POST.get('variation_id'):
        variation = get_object_or_404(ProductVariation, id=request.POST['variation_id'])

    quantity = int(request.POST.get('quantity', 1))

    cart, _ = Cart.objects.get_or_create(user=request.user)
    price = variation.price if variation else (
        product.variations.first().price if product.variations.exists() else product.price
    )

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        variation=variation,
        defaults={'unit_price': price, 'quantity': quantity}
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    return redirect('cart_view')


@login_required
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    qty = int(request.POST.get('quantity', 1))

    if 'variation_id' in request.POST:
        variation_id = request.POST.get('variation_id')
        variation = get_object_or_404(ProductVariation, id=variation_id)
        item.variation = variation
        item.unit_price = variation.price

    if qty <= 0:
        item.delete()
    else:
        item.quantity = qty
        item.save()

    return redirect('checkout_view')


@login_required
def checkout_view(request):
    cart = get_object_or_404(Cart, user=request.user)
    addresses = Address.objects.filter(user=request.user)

    subtotal = sum([item.line_total for item in cart.items.all()])
    # প্রতি product quantity এর উপর ভিত্তি করে shipping fee
    shipping_fee = sum([item.quantity * 50 for item in cart.items.all()])
    discount = 0
    grand_total = subtotal + shipping_fee - discount

    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'items': cart.items.all(),
        'addresses': addresses,
        'subtotal': subtotal,
        'shipping_fee': shipping_fee,
        'discount': discount,
        'grand_total': grand_total
    })

@login_required
def update_checkout_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    # Remove item if delete request
    if 'delete' in request.GET:
        item.delete()
        return redirect('checkout_view')

    if request.method == 'POST':
        qty = int(request.POST.get('quantity', 1))
        if qty <= 0:
            item.delete()
            return redirect('checkout_view')

        if request.POST.get('variation_id'):
            variation_id = request.POST['variation_id']
            variation = get_object_or_404(ProductVariation, id=variation_id)
            item.variation = variation
            item.unit_price = variation.price

        item.quantity = qty
        item.save()

    return redirect('checkout_view')


@login_required
def remove_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return redirect('cart_view')


@login_required
def place_order(request):
    cart = get_object_or_404(Cart, user=request.user)
    if not cart.items.exists():
        return redirect('cart_view')

    if request.method == 'POST':
        # Get address from form
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        country = request.POST.get('country')
        city = request.POST.get('city')
        postal_code = request.POST.get('postal_code')
        street = request.POST.get('street')

        if not all([name, email, phone, country, city, postal_code, street]):
            return redirect('checkout_view')

        address = Address.objects.create(
            user=request.user,
            full_name=name,
            phone=phone,
            line1=street,
            city=city,
            state='',
            postal_code=postal_code,
            country=country,
            is_shipping=True
        )

        subtotal = sum([item.line_total for item in cart.items.all()])
        shipping_fee = sum([item.quantity * 50 for item in cart.items.all()])
        discount = 0
        grand_total = subtotal + shipping_fee - discount

        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                address=address,
                subtotal=subtotal,
                shipping_fee=shipping_fee,
                discount=discount,
                grand_total=grand_total,
                status='confirmed',
                payment_status='pending'
            )
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    variation=item.variation,
                    quantity=item.quantity,
                    unit_price=item.unit_price
                )
            cart.items.all().delete()

        return redirect('order_detail', order_id=order.id)



@login_required
def order_list(request):
    if request.user.is_staff:
        orders = Order.objects.all().order_by('-created_at')
    else:
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    items = order.items.select_related('product', 'variation').prefetch_related('product__images')
    return render(request, 'orders/order_detail.html', {'order': order, 'items': items})
