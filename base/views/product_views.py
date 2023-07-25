from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.http import JsonResponse
from django.db.models import Q

from base.models import Product
from base.serializers import ProductSerializer

@api_view(['GET'])
@permission_classes([])
def getProducts(request):
    query_params = request.query_params
    query = query_params.get('keyword')
    
    if query is None or query.lower() == 'null':
        products= Product.objects.all()
    else:
        products = Product.objects.filter(name__icontains=query)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([])
def getProduct(request, pk):
    product = Product.objects.get(_id=pk)
    serializer = ProductSerializer(product, many=False)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([])
def getFilteredProducts(request):
    option = request.GET.get('options')
    category = request.GET.get('category')
    min_price = request.GET.get('minPrice')
    max_price = request.GET.get('maxPrice')
    sort_by = request.GET.get('sortBy')

    # Filter the products based on the provided parameters
    queryset = Product.objects.filter(options=option)
    
    print(category)

    if category:
        queryset = queryset.filter(category=category)

    if min_price:
        queryset = queryset.filter(price__gte=min_price)

    if max_price:
        queryset = queryset.filter(price__lte=max_price)

    if sort_by:
        if sort_by == 'lowest':
            queryset = queryset.order_by('price')
        elif sort_by == 'highest':
            queryset = queryset.order_by('-price')
        elif sort_by == 'newest':
            queryset = queryset.order_by('-createdAt')

    serializer = ProductSerializer(queryset, many=True)
    return JsonResponse(serializer.data, safe=False)