from django.shortcuts import render,redirect
from store.models import Category,Product,Cart,Tax,CartOrder,CartOrderItem,Review,Brand,Notification,Coupon
from store.serializer import CartSerializer, ProductListSerializer,ProductDetailSerializer,CategorySerializer,CartOrderSerializer,ReviewSerializer,BrandSerializer,CouponSerializer,ReviewSummarySerializer,Product2Serializer
from rest_framework import generics,status
from rest_framework.permissions import AllowAny 
from userauths.models import User
from decimal import Decimal
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .myfilter import ProductFilter
from .mypagination import ProductPagination
import stripe
from django.conf import settings
from django.db.models import Q
from django.http import Http404
from django.utils.translation import get_language
from django.utils.translation import gettext as _


# Create your views here.

stripe.api_key = settings.STRIPE_SECRET_KEY

def send_notification(user=None, vendor=None, order=None, order_item=None):
    Notification.objects.create(
        user=user,
        vendor=vendor,
        order=order,
        order_item=order_item
    )




class CategoryListAPIView(generics.ListAPIView):
    queryset=Category.objects.all()
    serializer_class= CategorySerializer
    permission_classes = [AllowAny]

    def get_serializer_context(self):
        # Pass the request object to the serializer context
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class BrandListAPIView(generics.ListAPIView):
    queryset=Brand.objects.all()
    serializer_class= BrandSerializer
    permission_classes = [AllowAny] 

    def get_serializer_context(self):
        # Pass the request object to the serializer context
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ProductBrandListAPIView(generics.ListAPIView):
    queryset=Product.objects.all()
    serializer_class= ProductListSerializer
    permission_classes = [AllowAny]
    pagination_class = ProductPagination

    # def get_queryset(self):
    #     name=self.kwargs.get('brand')
    #     currency_code = self.kwargs.get('currency')
    #     if name:
    #         brand= Brand.objects.get(title=name)
    #         queryset = Product.objects.filter(brand=brand)
    #     else: 
    #         queryset=Product.objects.all()    
    #     return queryset
    def get_queryset(self):
        name = self.kwargs.get('brand')
        currency_code = self.kwargs.get('currency')

        if currency_code not in ['EGP', 'AED']:
            raise Http404("Invalid currency code")

        if name:
            brand = Brand.objects.get(title_en=name)
            queryset = Product.objects.filter(brand=brand)
        else:
            queryset = Product.objects.all()

        if currency_code == 'EGP':
            queryset = queryset.exclude(price_EGP=0)
        else:
            queryset = queryset.exclude(price_AED=0)

        return queryset
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['currency_code'] = self.kwargs.get('currency')
        return context 


class ProductCategory(generics.ListAPIView):
    queryset=Product.objects.all()
    serializer_class= ProductListSerializer
    permission_classes = [AllowAny]
    pagination_class = ProductPagination

    # def get_queryset(self):
    #     name=self.kwargs.get('category')
    #     currency_code = self.kwargs.get('currency')
    #     if name:
    #         category= Category.objects.get(title=name)
    #         queryset = Product.objects.filter(category=category)
    #     else: 
    #         queryset=Product.objects.all()    
    #     return queryset
    def get_queryset(self):
        name = self.kwargs.get('category')
        currency_code = self.kwargs.get('currency')

        if currency_code not in ['EGP', 'AED']:
            raise Http404("Invalid currency code")

        if name:
            category = Category.objects.get(title_en=name)
            queryset = Product.objects.filter(category=category)
        else:
            queryset = Product.objects.all()

        if currency_code == 'EGP':
            queryset = queryset.exclude(price_EGP=0)
        else:
            queryset = queryset.exclude(price_AED=0)

        return queryset
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['currency_code'] = self.kwargs.get('currency')
        #context['request'] = self.request
        return context 


class ProductListAPIView(generics.ListAPIView):
    queryset=Product.objects.all()
    serializer_class= ProductListSerializer
    permission_classes = [AllowAny]
    pagination_class = ProductPagination

    filterset_class = ProductFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        currency_code = self.kwargs.get('currency')

        if currency_code not in ['EGP', 'AED']:
            raise Http404("Invalid currency code")  

        if currency_code == 'EGP':
            queryset = queryset.exclude(price_EGP=0)
        else:
            
            queryset = queryset.exclude(price_AED=0) 

        



        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['currency_code'] = self.kwargs.get('currency')
        return context



class ProductDetailAPIView(generics.RetrieveAPIView):
    serializer_class=ProductDetailSerializer
    permission_classes=[AllowAny]

    def get_object(self):
        slug=self.kwargs['slug']
        currency_code = self.kwargs.get('currency')
        try:
            return Product.objects.get(slug=slug)
        except Product.DoesNotExist:
            raise Http404("Product not found")

        # query = Product.objects.get(slug=slug)
        # return query


    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['currency_code'] = self.kwargs.get('currency')
        return context  






class ReviewListAPIView(generics.ListCreateAPIView):
    permission_classes = [AllowAny,]


    def get_complete_image_url(self, image_path):
        # Assuming BASE_URL is defined in your Django settings
        if isinstance(settings.BASE_URL, tuple):
            # Convert tuple to string
            base_url = ''.join(settings.BASE_URL)
        else:
            base_url = settings.BASE_URL
        return base_url + image_path
    
   

    def get_queryset(self):
        product_id = self.kwargs['product_id']
        product = Product.objects.get(id=product_id)
        reviews = Review.objects.filter(product=product)
        return reviews
    
    def list(self, request, *args, **kwargs):
        product_id = self.kwargs['product_id']
        product = Product.objects.get(id=product_id)

        reviews = Review.objects.filter(product=product)
        review_serializer = ReviewSerializer(reviews, many=True)


        for review in review_serializer.data:
            profile = review['profile']
            if profile and 'image' in profile:
                profile['image'] = self.get_complete_image_url(profile['image'])

        review_summary = {
            "one_star": reviews.filter(rating=1).count(),
            "two_star": reviews.filter(rating=2).count(),
            "three_star": reviews.filter(rating=3).count(),
            "four_star": reviews.filter(rating=4).count(),
            "five_star": reviews.filter(rating=5).count()
        }
        review_summary_serializer = ReviewSummarySerializer(data=review_summary)
        review_summary_serializer.is_valid()

        return Response({
            "reviews": review_serializer.data,
            "summary": review_summary_serializer.data
        })

    def create(self, request, *args, **kwargs):
        payload = request.data

        user_id = payload['user_id']
        product_id = payload['product_id']
        rating = payload['rating']
        review = payload['review']

        user = User.objects.get(id=user_id)
        product = Product.objects.get(id=product_id)

        Review.objects.create(
            user=user,
            product=product,
            rating=rating,
            review=review,
        )

        return Response({"message": "Review Created Successfully"}, status=status.HTTP_201_CREATED)


class CartAPIView(generics.ListCreateAPIView):
    queryset=Cart.objects.all()
    serializer_class=CartSerializer
    permission_classes=[AllowAny]  


    def create(self, request, *args, **kwargs):
        payload=request.data 

        product_id=payload['product_id']
        user_id=payload['user_id']
        qty=payload['qty']
        price=payload['price']
        currency=payload['currency']
        shipping_amount=payload['shipping_amount']
        country=payload['country']
        size=payload['size']
        color=payload['color']
        cart_id=payload['cart_id']


        product=Product.objects.get(id=product_id)

        if user_id != "undefined":
            user = User.objects.get(id=user_id)

        else:
            user = None 

        tax = Tax.objects.filter(country=country).first()
        if tax:
            tax_rate = tax.rate /100
        else:
            tax_rate = 0

        cart = Cart.objects.filter(cart_id=cart_id, product=product).first()

        if cart:
            cart.user=user
            cart.product=product
            cart.qty=qty
            cart.price=price
            cart.currency=currency
            cart.sub_total= Decimal(price) * int(qty)
            cart.shipping_amount = Decimal(shipping_amount) * int(qty)
            cart.tax_fee = int(qty) * Decimal(tax_rate)
            cart.color=color
            cart.size=size
            cart.country=country
            cart.cart_id=cart_id


            service_fee_percentage = 10 / 100
            cart.service_fee = Decimal(service_fee_percentage)  * cart.sub_total

            cart.total =cart.sub_total + cart.shipping_amount + cart.tax_fee
            cart.save()
            return Response({'message': _("Cart Updated Successfully")}, status=status.HTTP_200_OK)

        else:
            cart=Cart()
            cart.user=user
            cart.product=product
            cart.qty=qty
            cart.price=price
            cart.currency=currency
            cart.sub_total= Decimal(price) * int(qty)
            cart.shipping_amount = Decimal(shipping_amount) * int(qty)
            cart.tax_fee = int(qty) * Decimal(tax_rate)
            cart.color=color
            cart.size=size
            cart.country=country
            cart.cart_id=cart_id


            service_fee_percentage = 10 / 100
            cart.service_fee = Decimal(service_fee_percentage) * cart.sub_total

            cart.total =cart.sub_total + cart.shipping_amount + cart.tax_fee
            cart.save()
            return Response({'message': _("Cart Created Successfully")}, status=status.HTTP_201_CREATED)



class CartListView(generics.ListAPIView):
    serializer_class=CartSerializer
    queryset= Cart.objects.all()
    permission_classes=[AllowAny,]


    def get_queryset(self):
        cart_id = self.kwargs['cart_id']
        user_id = self.kwargs.get('user_id')


        if user_id is not None:
            user = User.objects.get(id=int(user_id))
            queryset = Cart.objects.filter(user=user, cart_id=cart_id)
        else:
            queryset = Cart.objects.filter(cart_id=cart_id)
        return queryset    


class CartDetailView(generics.RetrieveAPIView):
    serializer_class=CartSerializer
    queryset= Cart.objects.all()
    permission_classes=[AllowAny,]


    def get_queryset(self):
        cart_id = self.kwargs['cart_id']
        user_id = self.kwargs.get('user_id')


        if user_id is not None:
            user = User.objects.get(id=int(user_id))
            queryset = Cart.objects.filter(user=user, cart_id=cart_id)
        else:
            queryset = Cart.objects.filter(cart_id=cart_id)
        return queryset  
    

    def get(self,*args, **kwargs):
        queryset=self.get_queryset()

        total_shipping = 0.0
        total_tax = 0.0
        total_service_fee = 0.0
        total_subtotal = 0.0
        total_total = 0.0


        for cart_item in queryset:
            total_shipping += float(self.calculate_shipping(cart_item))
            total_tax += float(self.calculate_tax(cart_item))
            total_service_fee += float(self.calculate_service_fee(cart_item))
            total_subtotal += float(self.calculate_subtotal(cart_item))
            total_total += float(self.calculate_total(cart_item))



        data = {
            'shipping': total_shipping,
            'tax': total_tax,
            'service_fee': total_service_fee,
            'sub_total': total_subtotal,
            'total': round(total_total,2),
        } 

        return Response(data)   



    def calculate_shipping(self,cart_item):
        return cart_item.shipping_amount
    def calculate_tax(self,cart_item):
        return cart_item.tax_fee
    def calculate_service_fee(self,cart_item):
        return cart_item.service_fee
    def calculate_subtotal(self,cart_item):
        return cart_item.sub_total
    def calculate_total(self,cart_item):
        return cart_item.total        


class CartItemDeleteAPIView(generics.DestroyAPIView):
    serializer_class=CartSerializer
    lookup_field='cart_id'

    def get_object(self, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        item_id = self.kwargs['item_id']
        cart_id = self.kwargs['cart_id']

        if user_id:
            user =User.objects.get(id=user_id)
            cart = Cart.objects.get(id=item_id, user=user, cart_id=cart_id)
        else:
            cart = Cart.objects.get(id=item_id, cart_id=cart_id)    


        return cart
    
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': _('Item deleted successfully.')}, status=status.HTTP_204_NO_CONTENT)
    


class CreateOrderAPIView(generics.CreateAPIView):
    serializer_class = CartOrderSerializer  
    queryset = CartOrder.objects.all()
    permission_classes= [AllowAny,]  


    def create(self, request, *args, **kwargs):
        payload = request.data


        fullname = payload['full_name']
        mobile = payload['mobile']
        address = payload['address']
        state = payload['state']
        city = payload['city']
        country = payload['country']
        email = payload['email']

        cart_id = payload['cart_id']
        user_id = payload['user_id']

        cart_order_id=payload['cart_id']
        print(f"user id ======== {user_id}")

        if user_id == 0:
            
            user=None
        else:
            user=User.objects.get(id=user_id)

        print(f"user  ======== {user}")    
            

        cart_items = Cart.objects.filter(cart_id=cart_id)

        total_shipping = Decimal(0.00)
        total_tax = Decimal(0.00)
        total_service_fee = Decimal(0.00)
        total_subtotal = Decimal(0.00)
        total_total = Decimal(0.00)

        order = CartOrder.objects.create(

        buyer=user,
        full_name =fullname, 
        mobile =mobile,
        address = address, 
        state = state, 
        city = city, 
        country = country,  
        email = email, 
        cart_order_id=cart_order_id,
        payment_status="pending", 

        )


        for c in cart_items:
            CartOrderItem.objects.create(
                order=order,
                product=c.product,
                vendor = c.product.vendor,
                qty=c.qty,
                price=c.price,
                currency=c.currency,
                sub_total= c.sub_total,
                shipping_amount = c.shipping_amount,
                tax_fee = c.tax_fee,
                color=c.color,
                size=c.size,
                country=c.country,
                total = c.total,
                initial_total =c.total,


            )

            total_shipping += Decimal(c.shipping_amount) 
            total_tax += Decimal(c.tax_fee) 
            total_service_fee += Decimal(c.service_fee) 
            total_subtotal += Decimal(c.sub_total) 
            total_total += Decimal(c.total)


            order.vendor.add(c.product.vendor)

        order.sub_total= total_subtotal
        order.shipping_amount = total_shipping
        order.tax_fee =total_tax
        order.service_fee = total_service_fee
        order.total=total_total
        order.initial_total=total_total

        order.save()

        return Response({"message": _("Order created successfully"), "order_oid":order.oid}, status=status.HTTP_201_CREATED)     


class CheckoutView(generics.RetrieveAPIView):
    serializer_class= CartOrderSerializer
    lookup_field ='order_oid'

    def get_object(self):
        order_oid = self.kwargs['order_oid']
        order = CartOrder.objects.get(oid=order_oid)
        return order
    





######################################################



class CouponAPIView(generics.CreateAPIView):
    serializer_class= CouponSerializer
    queryset = Coupon.objects.all()
    permission_classes = [AllowAny,]




    def create(self,request):
        payload = request.data

        order_oid = payload['order_oid']
        coupon_code = payload['coupon_code']


        order = CartOrder.objects.get(oid=order_oid)
        coupon = Coupon.objects.filter(code=coupon_code).first()

        if coupon:
            order_items = CartOrderItem.objects.filter(order=order, vendor=coupon.vendor)

            if order_items:
                for i in order_items:
                    if not coupon in i.coupon.all():
                        discount = i.total * coupon.discount / 100

                        i.total -= discount
                        i.sub_total -= discount
                        i.coupon.add(coupon)
                        i.saved += discount

                        order.total -= discount
                        order.sub_total -= discount
                        order.saved -= discount

                        i.save()
                        order.save()

                        return Response({"message":"Coupon Activated", "icon":"success"}, status=status.HTTP_200_OK)
                    else:
                        return Response({"message":"Coupon Already Activated", "icon":"warning"}, status=status.HTTP_200_OK)
            else:
                return Response({"message":"Order Item Does Not Exists", "icon":"error"}, status=status.HTTP_200_OK)
        else:
            return Response({"message":"Coupon Does Not Exists", "icon":"error"}, status=status.HTTP_200_OK)
    



class StripeCheckoutView(generics.CreateAPIView):
    serializer_class =CartOrderSerializer
    queryset = CartOrder.objects.all()
    permission_classes = [AllowAny,]



    def create(self,*args, **kwargs):
        order_oid = self.kwargs['order_oid']
        cart_id = self.kwargs['cart_id']

        link_url = self.request.data['link']

        order = CartOrder.objects.get(oid=order_oid)

      


        if not order:
            return Response({"message":"Order Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            checkout_session =stripe.checkout.Session.create(
                customer_email = order.email,
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data':{
                            'currency':'usd',
                            'product_data':{
                                'name':order.full_name,
                            },
                            'unit_amount': int(order.total * 100)
                        },
                        'quantity':1,
                    }
                ],
                mode='payment',
                # success_url ='https://levado.netlify.app/payment-success/' + order.oid + '?session_id={CHECKOUT_SESSION_ID}',
                # cancel_url ='https://levado.netlify.app/payment-failed/?session_id={CHECKOUT_SESSION_ID}'

                success_url = f'{link_url}/payment-success/{order.oid}?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url = f'{link_url}/payment-failed/?session_id={{CHECKOUT_SESSION_ID}}'

                

            )

            order.stripe_session_id = checkout_session.stripe_id
            order.save()
            #carts.delete()

            return redirect(checkout_session.url)
        except stripe.error.StripeError as e:
            return Response({"error": f"Something went wrong while creating the checkout session: {str(e)}"})


class PaymentSuccessView(generics.CreateAPIView):
    serializer_class =CartOrderSerializer
    queryset = CartOrder.objects.all()
    permission_classes = [AllowAny,]


    def create(self, request, *args, **kwargs):
        payload = request.data

        order_oid =payload['order_oid']
        session_id = payload['session_id']

        order = CartOrder.objects.get(oid=order_oid)

        order_items = CartOrderItem.objects.filter(order=order)

        cart_id = order.cart_order_id

        carts = Cart.objects.filter(cart_id=cart_id)


        if session_id != 'null':
            session = stripe.checkout.Session.retrieve(session_id)

            if session.payment_status == "paid":
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
    
                   
                    return Response({"message":"Payment Successfull"})
                else:
                    return Response({"message":"Already Paid"})

            elif session.payment_status == "unpaid":
                return Response({"message":"Your Invoice is Unpaid"}) 
            elif session.payment_status == "cancelled":
                return Response({"message":"Your Invoice was canceled"})
            else:
                return Response({"message":"An Error Occured, Try Again..."})
        else:
            session = None   








class Fpro(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    pagination_class = ProductPagination

    def get_queryset(self):
        currency_code = self.kwargs.get('currency','')

        # if currency_code == 'EGP':
        #     queryset = Product.objects.select_related('category','brand','vendor').prefetch_related('specification__set','gallery__set','color__set','size__set').exclude(price_AED=0)
        # elif currency_code == 'AED':
        #     queryset = Product.objects.select_related('category','brand','vendor').prefetch_related('specification__set','gallery__set','color__set','size__set').exclude(price_EGP=0)
        # else:
            # If the currency is not supported, you can handle it here
        queryset = Product.objects.all().select_related('category','brand','vendor').prefetch_related('specification__set','gallery__set','color__set','size__set')

        brand_ids_str = self.request.query_params.get('brand_ids')
        category_ids_str = self.request.query_params.get('category_ids')
        prices_str = self.request.query_params.get('price')
        rating_str = self.request.query_params.get('rating')
        title_query = self.request.query_params.get('title')

        lang = get_language()

        brand_ids = []
        category_ids = []
        prices = []
        min_price = None
        max_price = None
        rating = None

        if brand_ids_str:
            if brand_ids_str != '[]':
                brand_ids = [int(id) for id in brand_ids_str.strip('[]').split(',')]
        
        if category_ids_str:
            if category_ids_str != '[]':
                category_ids = [int(id) for id in category_ids_str.strip('[]').split(',')]

        if prices_str:
            prices = [float(price) for price in prices_str.split(',')]
            min_price, max_price = prices[0], prices[1] if len(prices) > 1 else None 
            


        if rating_str:
            if rating_str != '' and int(rating_str) != 0:
                rating = int(rating_str)


        if brand_ids:
            queryset = queryset.filter(brand__id__in=brand_ids)

        if category_ids:
            queryset = queryset.filter(category__id__in=category_ids)

        if min_price is not None and max_price is not None:
            if currency_code == 'EGP':
                queryset = queryset.filter(price_EGP__range=(min_price, max_price))
            else:
                queryset = queryset.filter(price_AED__range=(min_price, max_price))

        if rating is not None:
            queryset = queryset.filter(rating__gte=rating)

        if title_query:
            if lang == 'ar':
                queryset = queryset.filter(title_ar__icontains=title_query)
            elif lang == 'en':
                queryset = queryset.filter(title_en__icontains=title_query)
            else:
                queryset = queryset.none()

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['currency_code'] = self.kwargs.get('currency')
        return context








class PopularProductsAPIView(generics.ListAPIView):
    serializer_class = ProductListSerializer

    def get_queryset(self):
        currency_code = self.kwargs.get('currency')
        queryset = Product.objects.all()
        if currency_code not in ['EGP', 'AED']:
            raise Http404("Invalid currency code")


        if currency_code == 'EGP':
            queryset = queryset.exclude(price_EGP=0)
        else:
            queryset = queryset.exclude(price_AED=0)        

        # Sort products based on sales count (orders)
        queryset = sorted(queryset, key=lambda p: p.product_rating() or 0, reverse=True)


        # Return the top 10 products
        return queryset[:10]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['currency_code'] = self.kwargs.get('currency')
        return context 
    




class BestSellerProductsAPIView(generics.ListAPIView):
    serializer_class = ProductListSerializer

    def get_queryset(self):
        currency_code = self.kwargs.get('currency')
        queryset = Product.objects.all()
        if currency_code not in ['EGP', 'AED']:
            raise Http404("Invalid currency code")


        if currency_code == 'EGP':
            queryset = queryset.exclude(price_EGP=0)
        else:
            queryset = queryset.exclude(price_AED=0)        

        # Sort products based on sales count (orders)
        queryset = sorted(queryset, key=lambda p: p.orders() or 0 , reverse=True)


        # Return the top 10 products
        return queryset[:10]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['currency_code'] = self.kwargs.get('currency')
        return context 
    



     

             



from rest_framework.views import APIView


class ProductCreateAPIView(APIView):
    def post(self, request):
        serializer = Product2Serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = Product2Serializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)        