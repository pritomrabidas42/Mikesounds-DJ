from django.shortcuts import render, get_object_or_404
from .models import Product, Slider, AdsBanner
from django.db.models import Q

def product_list(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(status=True)
    if query:
        products = products.filter(
            Q(title__icontains=query) |
            Q(brand__name__icontains=query)
        )
    products = products.prefetch_related('images', 'brand')

    sliders = Slider.objects.filter(status=True)
    ads = AdsBanner.objects.filter(status=True)

    context = {
        'products': products,
        'query': query,
        'sliders': sliders,
        'ads': ads,
    }
    return render(request, 'products/product_list.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, status=True)
    sliders = Slider.objects.filter(status=True)
    ads = AdsBanner.objects.filter(status=True)
    return render(request, 'products/product_detail.html', {
        'product': product,
        'sliders': sliders,
        'ads': ads
    })
