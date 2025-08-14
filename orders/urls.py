from django.urls import path
from .views import *

urlpatterns = [
    path('cart/', cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/add/<int:product_id>/<int:variation_id>/', add_to_cart, name='add_to_cart_variation'),
    path('cart/update/<int:item_id>/', update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', remove_cart_item, name='remove_cart_item'),
    path('checkout/', checkout_view, name='checkout_view'),
    path('checkout/update/<int:item_id>/', update_checkout_cart, name='update_checkout_cart'),
    path('place-order/', place_order, name='place_order'),
    path('orders/', order_list, name='order_list'),
    path('orders/<int:order_id>/', order_detail, name='order_detail'),
]
