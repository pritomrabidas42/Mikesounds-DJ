from django.urls import path
from .views import payment_init, payment_callback

urlpatterns = [
    path('init/<int:order_id>/<str:gateway>/', payment_init, name='payment_init'),
    path('callback/<int:txn_id>/', payment_callback, name='payment_callback'),
]
