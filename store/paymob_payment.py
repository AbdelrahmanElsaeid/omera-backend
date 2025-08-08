import hashlib
import hmac
import os

import requests
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from store.models import Cart, CartOrder, CartOrderItem, Notification
from store.serializer import CartOrderSerializer

API_KEY = os.environ.get('PAYMOB_API_KEY')
FRONTEND_URL = os.environ.get('FRONTEND_BASE_URL')


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

        try:  
            order_data = create_order(token,grand_total, order_oid)
        except:
            return Response({"message": "An error occurred while creating the order. Please login again and try to pay."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
        # Perform the third step to generate the payment token 

        if payment_method =="card":
            integration_id=int(os.environ.get('CARD_INTEGRATION_ID'))
        elif payment_method =="wallet":
            integration_id=int(os.environ.get('WALLET_INTEGRATION_ID')) 
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


        key = os.environ.get('PAYMOB_HMACK_KEY')
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
    
                
                    redirect_url = f'{FRONTEND_URL}/payment-success/{merchant_order_id}'
                    return HttpResponseRedirect(redirect_url)
                else:
                    return Response({"message":"Already Paid"})

            elif success == "false":
                redirect_url = f'{FRONTEND_URL}/payment/fail/'
                return HttpResponseRedirect(redirect_url) 
            else:
                redirect_url = f'{FRONTEND_URL}/payment/fail/'
                return HttpResponseRedirect(redirect_url)                
        
        else:
            
            redirect_url = f'{FRONTEND_URL}/payment/fail/'
            return HttpResponseRedirect(redirect_url)



class CheckPaymentView(APIView):
    serializer_class = CartOrderSerializer
    permission_classes = [AllowAny]

class CheckPaymentView(APIView):
    serializer_class = CartOrderSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        order_oid = self.kwargs['order_oid']
        order = CartOrder.objects.get(oid=order_oid)
        return Response({"message": "Payment Successfull","status": order.payment_status},status=status.HTTP_200_OK)

    


      