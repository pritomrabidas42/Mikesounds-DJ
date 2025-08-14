from django.shortcuts import render, get_object_or_404
from .models import Product
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
    context = {'products': products, 'query': query}
    return render(request, 'products/product_list.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, status=True)
    return render(request, 'products/product_detail.html', {'product': product})
