from django.shortcuts import render,redirect
from store.models import Category,Product,Cart,Tax,CartOrder,CartOrderItem,Coupon,Notification,Review
from store.serializer import CartSerializer, ProductSerializer,CategorySerializer,CartOrderSerializer,CouponSerializer,NotificationSerializer,ReviewSerializer,Product2Serializer
from rest_framework import generics,status
from rest_framework.permissions import AllowAny 
from userauths.models import User
from decimal import Decimal
from rest_framework.response import Response
import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
import hashlib
import os
import hmac
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
import requests
import json

API_KEY = 'ZXlKaGJHY2lPaUpJVXpVeE1pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SmpiR0Z6Y3lJNklrMWxjbU5vWVc1MElpd2ljSEp2Wm1sc1pWOXdheUk2T1RJNU9EQXlMQ0p1WVcxbElqb2lhVzVwZEdsaGJDSjkuSTBwN1VTQVBaZl9FRHhrLS1XUzl1LXJsSTBwOGpTenE4WUNmSVkyTmhyYU9fOHZVZHVhS3NqcDZVYVkwMU1lS1dzS3VhRG5PMk9ySHAxVF9rdThNU1E='  # your API key here


def send_notification(user=None, vendor=None, order=None, order_item=None):
    Notification.objects.create(
        user=user,
        vendor=vendor,
        order=order,
        order_item=order_item
    )


def get_auth_token():
        data = {"api_key": API_KEY}
        response = requests.post('https://accept.paymob.com/api/auth/tokens', json=data)
        response.raise_for_status()
        
        return response.json()['token']
    



def create_order(token, grand_total, order_oid):
    data = {
        "auth_token": token,
        "delivery_needed": "false",
        "amount_cents": grand_total,
        "merchant_order_id": order_oid,
        "currency": "EGP",
        "items": [],
    }
    response = requests.post('https://accept.paymob.com/api/ecommerce/orders', json=data)
    response.raise_for_status()
    return response.json()#['id']

def generate_payment_token(token,order_data,order,integration_id):
    data = {
        "auth_token": token,
        "amount_cents": order_data['amount_cents'],
        "expiration": 36000,
        "order_id": order_data['id'],
        "billing_data": {
            "first_name": order.full_name,
            "last_name": order.full_name,
            "phone_number": order.mobile, 
            "email": order.email,
            "apartment": "NA",
            "floor": "NA",
            "street": order.address,
            "building": "NA",
            "shipping_method": "NA",
            "postal_code": order.mobile,
            "city": order.city,
            "state": order.state if order.state else "NA",
            "country": order.country
        },
        "currency": "EGP",
        "integration_id": integration_id
    }
    response = requests.post('https://accept.paymob.com/api/acceptance/payment_keys', json=data)
    response.raise_for_status()
    return response.json()['token']


def card_payment(payment_token):
    iframe_url = f'https://accept.paymob.com/api/acceptance/iframes/796301?payment_token={payment_token}'



def wallet_mobile(phone_num,payment_token):
    response_pay = requests.post(
            'https://accept.paymob.com/api/acceptance/payments/pay',
            headers={'content-type': 'application/json'},
            json={
                "source": {
                    "identifier": phone_num,
                    "subtype": "WALLET"
                },
                "payment_token": payment_token
            }
        )
    return  response_pay.json()['iframe_redirection_url']




class PaymobPaymentView(APIView):

    def get(self, request, order_oid, payment_method):


        phone_num = request.query_params.get('phone_num')
    

    
        order = CartOrder.objects.get(oid=order_oid)

        grand_total = float(order.total * 100)

                
        # Perform the first step to obtain the token
        token = get_auth_token()

        
        # Perform the second step to create the order   
        #order_data = create_order(token,grand_total, order_oid)

        try:  
            order_data = create_order(token,grand_total, order_oid)
        except:
            return Response({"message": "An error occurred while creating the order. Please login again and try to pay."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

        # Perform the third step to generate the payment token 

        if payment_method =="card":
            integration_id=4302305
        elif payment_method =="wallet":
            integration_id=4566028 
        else:
            return Response({"message":"Payment Method Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
         

        payment_token = generate_payment_token(token,order_data,order,integration_id)


        if payment_method =="card":
            card_payment(payment_token)

            #Redirect to the payment URL
            payment_url = f"https://accept.paymob.com/api/acceptance/iframes/796301?payment_token={payment_token}"

            return redirect(payment_url)
        elif payment_method =="wallet":
            redirect_url=wallet_mobile(phone_num, payment_token)
            return redirect(redirect_url)
        else:
            return Response({"message":"Payment Method Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({"message": "Request processed successfully"}, status=status.HTTP_200_OK)

    
class PaymobCallbackView(APIView):
    
   

    @csrf_exempt
    def get(self, request, *args, **kwargs):
        # Extract the HMAC value from the query parameters
        received_hmac = request.query_params.get('hmac')

        # print(f"amount_cents:{request.query_params.get('amount_cents')}")
        # print(f"created_at:{request.query_params.get('created_at')}")
        # print(f"currency:{request.query_params.get('currency')}")
        # print(f"error_occured:{request.query_params.get('error_occured')}")
        # print(f"has_parent_transaction:{request.query_params.get('has_parent_transaction')}")
        # print(f"obj.id:{request.query_params.get('id')}")
        # print(f"integration_id:{request.query_params.get('integration_id')}")
        # print(f"is_3d_secure:{request.query_params.get('is_3d_secure')}")
        # print(f"is_auth:{request.query_params.get('is_auth')}")
        # print(f"is_capture:{request.query_params.get('is_capture')}")
        # print(f"is_refunded:{request.query_params.get('is_refunded')}")
        # print(f"is_standalone_payment:{request.query_params.get('is_standalone_payment')}")
        # print(f"is_voided:{request.query_params.get('is_voided')}")
        # print(f"order.id:{request.query_params.get('order')}")
        # print(f"owner:{request.query_params.get('owner')}")
        # print(f"pending:{request.query_params.get('pending')}")
        # print(f"source_data.pan:{request.query_params.get('source_data.pan')}")
        # print(f"source_data.sub_type:{request.query_params.get('source_data.sub_type')}")
        # print(f"source_data.type:{request.query_params.get('source_data.type')}")
        # print(f"success:{request.query_params.get('success')}")


        # Sort the received data by key in lexicographical order
        sorted_data = sorted(request.query_params.items())

        # Concatenate the values of relevant keys into a single string
        relevant_keys = [
            'amount_cents', 'created_at', 'currency', 'error_occured', 'has_parent_transaction',
            'id', 'integration_id', 'is_3d_secure', 'is_auth', 'is_capture', 'is_refunded',
            'is_standalone_payment', 'is_voided', 'order', 'owner', 'pending', 'source_data.pan',
            'source_data.sub_type', 'source_data.type', 'success'
        ]
        concatenated_string = ''.join(str(value) for key, value in sorted_data if key in relevant_keys)

        # Debugging: Print concatenated string

        # print("Concatenated String:", concatenated_string)


        key = '53BA55760BB68D9EFE1BB7788CECA8FF'
        computed_hmac = hmac.new(key.encode(),concatenated_string.encode(),hashlib.sha512).hexdigest()

        

        # Compare the computed HMAC with the received HMAC
        if computed_hmac == received_hmac:
            # HMAC authentication successful
            #return Response("secure")
            merchant_order_id = request.query_params.get('merchant_order_id')
        
            order = CartOrder.objects.get(oid=merchant_order_id)

            order_items = CartOrderItem.objects.filter(order=order)

            cart_id = order.cart_order_id

            carts = Cart.objects.filter(cart_id=cart_id)

            success= request.query_params.get('success')


            if success == "true":
                
                if order.payment_status == "pending":
                    order.payment_status = "paid"
                    order.save()
                    carts.delete()

                    #send notification to customers
                    if order.buyer != None:
                        send_notification(user=order.buyer, order=order)

                    #send notification to vendor
                    for o in order_items:
                        send_notification(vendor=o.vendor, order=order, order_item=o)    
    
                
                    #return Response({"message":"Payment Successfull"})
                    redirect_url = 'http://localhost:4200/payment/success/'
                    return HttpResponseRedirect(redirect_url)
                else:
                    return Response({"message":"Already Paid"})

            elif success == "false":
                #return Response({"message":"Your Invoice is Unpaid"})
                redirect_url = 'http://localhost:4200/payment/fail/'
                return HttpResponseRedirect(redirect_url) 
            else:
                #return Response({"message":"An Error Occured, Try Again..."}) 
                redirect_url = 'http://localhost:4200/payment/fail/'
                return HttpResponseRedirect(redirect_url)                
        
        else:
            #print("Received HMAC:", received_hmac)
            #return Response("not secure")
            redirect_url = 'http://localhost:4200/payment/fail/'
            return HttpResponseRedirect(redirect_url)





      