
from django.shortcuts import render,redirect
from store.models import Category,Product,Cart,Tax,CartOrder,CartOrderItem,Coupon,Notification,Review,Wishlist
from store.serializer import CartSerializer, ProductDetailSerializer,CategorySerializer,CartOrderSerializer,WishlistListSerializer,NotificationSerializer,ReviewSerializer,WishlistSerializer
from rest_framework import generics,status
from rest_framework.permissions import AllowAny 
from userauths.models import User
from decimal import Decimal
from rest_framework.response import Response
from django.http import Http404
from django.conf import settings
from django.shortcuts import get_object_or_404

from django.db.models import F, FloatField, ExpressionWrapper
from django.db.models.functions import Coalesce
from django.utils.translation import gettext as _

# Create your views here.

class OrderAPIView(generics.ListAPIView):
    serializer_class=CartOrderSerializer
    permission_classes=[AllowAny,]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = User.objects.get(id=user_id)

        orders = CartOrder.objects.filter(buyer=user, payment_status = "paid")

        return orders
    

class OrderDetailAPIView(generics.RetrieveAPIView):
    serializer_class=CartOrderSerializer
    permission_classes=[AllowAny,]

    def get_object(self):
        user_id = self.kwargs['user_id']
        order_oid = self.kwargs['order_oid']
        user = User.objects.get(id=user_id)

        orders = CartOrder.objects.get(buyer=user,oid=order_oid, payment_status = "paid")

        return orders    
    



class WishlistCreateAPIView(generics.CreateAPIView):
    serializer_class = WishlistListSerializer
    permission_classes = (AllowAny, )

    def get_user_wishlist_product_ids(self, user):
        user_wishlist = Wishlist.objects.filter(user=user)
        return list(user_wishlist.values_list('product_id', flat=True))
    
    def get_complete_image_url(self, image_path):
        # Assuming BASE_URL is defined in your Django settings
        if isinstance(settings.BASE_URL, tuple):
            # Convert tuple to string
            base_url = ''.join(settings.BASE_URL)
        else:
            base_url = settings.BASE_URL
        return base_url + image_path
    
    # def get_user_wishlist_product(self, user):
    #     user_wishlist = Wishlist.objects.filter(user=user)
    #     return user_wishlist

    def create(self, request):
        payload = request.data 
        product_id = payload.get('product_id')
        user_id = payload.get('user_id')

        if  product_id is not None:

            user = get_object_or_404(User, id=user_id)
            product = get_object_or_404(Product, id=product_id)
            user_wishlist = Wishlist.objects.filter(user=user)


            wishlist_exists = Wishlist.objects.filter(product=product, user=user).exists()

            if wishlist_exists:
                Wishlist.objects.filter(product=product, user=user).delete()
                message = _("Removed From Wishlist")
            else:
                Wishlist.objects.create(product=product, user=user)
                message = _("Added To Wishlist")

            wishlist_product_ids = self.get_user_wishlist_product_ids(user)

            #wishlist_data = self.get_user_wishlist_product(user)

            #serialized_wishlist = self.serializer_class(user_wishlist, many=True).data

            serialized_wishlist = WishlistListSerializer(user_wishlist, many=True).data

            for item in serialized_wishlist:
                item['product']['image'] = self.get_complete_image_url(item['product']['image'])
            

            return Response({"message": message, "wishlist": wishlist_product_ids, "data": serialized_wishlist}, status=status.HTTP_200_OK if wishlist_exists else status.HTTP_201_CREATED)
        
        else:
            user = get_object_or_404(User, id=user_id)
            user_wishlist = Wishlist.objects.filter(user=user)
            wishlist_product_ids = self.get_user_wishlist_product_ids(user)

            serialized_wishlist = WishlistListSerializer(user_wishlist, many=True).data

            for item in serialized_wishlist:
                item['product']['image'] = self.get_complete_image_url(item['product']['image'])
            return Response({"message": _("Get Wishlist"), "wishlist": wishlist_product_ids, "data": serialized_wishlist}, status=status.HTTP_200_OK )



class WishlistAPIView(generics.ListAPIView):
    serializer_class = WishlistListSerializer
    permission_classes = (AllowAny, )

   
    def get_queryset(self):
            user_id = self.kwargs['user_id']
            currency_code = self.kwargs.get('currency')

            user = User.objects.get(id=user_id)
            queryset = Wishlist.objects.filter(user=user)

            if currency_code not in ['EGP', 'AED']:
                raise Http404("Invalid currency code")

            if currency_code == 'EGP':
                price_field = 'product__price_EGP'
            else:
                price_field = 'product__price_AED'

            # Annotate each product with the converted price based on the selected currency
            queryset = queryset.annotate(
                price=ExpressionWrapper(
                    Coalesce(F(price_field), 0),
                    output_field=FloatField()
                )
            )

            return queryset
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['currency_code'] = self.kwargs.get('currency')
        return context 
        




class NotificationListAPIView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes=[AllowAny,]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = User.objects.get(id=user_id)

        notif = Notification.objects.filter(user=user, seen=False)

        return notif



class MarkCustomerNotificationAsSeen(generics.RetrieveAPIView):
    serializer_class = NotificationSerializer
    permission_classes=[AllowAny,]

    def get_object(self):
        user_id = self.kwargs['user_id']
        noti_id = self.kwargs['noti_id']

        user = User.objects.get(id=user_id)
        noti = Notification.objects.get(id=noti_id, user=user)

        if noti.seen != True:
            noti.seen = True
            noti.save()

        return noti