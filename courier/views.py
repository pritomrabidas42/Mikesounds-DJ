from django.shortcuts import render
from .models import CourierAssignment, Courier
from django.contrib.auth.decorators import login_required

@login_required
def courier_report(request):
    assignments = CourierAssignment.objects.select_related('courier', 'order').order_by('-assigned_at')
    couriers = Courier.objects.filter(is_active=True)

    # Filtering
    start = request.GET.get('start')
    end = request.GET.get('end')
    courier_id = request.GET.get('courier')

    if start:
        assignments = assignments.filter(assigned_at__date__gte=start)
    if end:
        assignments = assignments.filter(assigned_at__date__lte=end)
    if courier_id:
        assignments = assignments.filter(courier__id=courier_id)

    return render(request, 'courier/report.html', {'assignments': assignments, 'couriers': couriers})
