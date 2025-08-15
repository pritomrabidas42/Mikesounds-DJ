from django.urls import path
from .views import courier_report

urlpatterns = [
    path('report/', courier_report, name='courier_report'),
]
