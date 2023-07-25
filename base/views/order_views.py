#! /usr/bin/env python3.6
from django.conf import settings
from django.http import JsonResponse ,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
import pytz

import json
import stripe

from base.models import Product,Order,OrderItem,ShippingAddress, User
from base.serializers import OrderSerializer



stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
def create_payment(request):
    # Retrieve the total amount from the request
    body = request.body.decode('utf-8')
    data = json.loads(body)
    amount = data.get('amount')

    # Create a payment intent on Stripe
    intent = stripe.PaymentIntent.create(
        amount=int(amount),
        currency='nzd',
        metadata={
        'order_items': data.get('order_items'),
        'shipping_address': data.get('shipping_address'),
        'items_price':data.get('items_price'),
        'shipping_price':data.get('shipping_price'),
        'total_price':data.get('total_price'),
        'user': data.get('user'),
    },
    )

    return JsonResponse({
        'clientSecret': intent.client_secret
    })

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.headers.get('stripe-signature')

    current_time = datetime.now(pytz.utc)
    nzst = pytz.timezone('Pacific/Auckland')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )

        data = event['data']
        event_type = event['type']

        if event_type == 'payment_intent.succeeded':
            # Handle successful payment event
            payment_intent = event['data']['object']
            amount = payment_intent['amount']
            order_items = json.loads(payment_intent['metadata']['order_items'])
            shipping_address = json.loads(payment_intent['metadata']['shipping_address'])
            shipping_price = payment_intent['metadata']['shipping_price']
            total_price = payment_intent['metadata']['total_price']
            user_id = payment_intent['metadata']['user']
            print('Payment Intent Received: ', amount, order_items, shipping_address, total_price, user_id )

            order = Order.objects.create(
                user= User.objects.get(id=user_id),
                shippingPrice= shipping_price,
                totalPrice= total_price,
                isPaid = True,
                paidAt = current_time.astimezone(nzst),
            )
            shipping = ShippingAddress.objects.create(
            order= order,
            address= shipping_address['address'],
            city= shipping_address['city'],
            postcode= shipping_address['postcode']
            )
            
            for i in order_items:
                product = Product.objects.get(_id=i['product'])

                item = OrderItem.objects.create(
                    product= product,
                    order= order,
                    name= product.name,
                    qty= i['qty'],
                    price= i['price'],
                    image= product.image.url,
                )

        return HttpResponse(status=200)
    
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getMyOrders(request):
    user = request.user
    orders = user.order_set.all()
    serializer= OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOrderById(request,pk):
    user = request.user
    try:
        order = Order.objects.get(_id=pk)
        if user.is_staff or order.user == user:
            serializer = OrderSerializer(order, many=False)
            return Response(serializer.data)
        else:
            Response({'detail':'Not Authorized'}, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({'detail':'Order does not exist'}, status=status.HTTP_400_BAD_REQUEST)
