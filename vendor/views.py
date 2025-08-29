
from datetime import datetime, timedelta

from django.conf import settings
from django.db import models, transaction
from django.db.models import F, Prefetch, Q, Sum
from django.db.models.functions import ExtractMonth
from django.utils.translation import gettext as _
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from store.models import (
    CartOrder,
    CartOrderItem,
    Color,
    Coupon,
    Gallery,
    Notification,
    Product,
    Review,
    Size,
    Specification,
)
from store.serializer import (
    CartOrderItemSerializer,
    CartOrderItemVendorSerializer,
    CartOrderVendorAllOrdersSerializer,
    ChangeOrderStatusSerializer,
    ColorAddSerializer,
    ColorSerializer,
    ColorUpdateSerializer,
    CombinedTotalsSerializer,
    CouponSerializer,
    CouponSummarySerializer,
    EarningSerializer,
    GallerySerializer,
    NotificationSerializer,
    NotificationSummarySerializer,
    ProductAddSerializer,
    ProductSerializer,
    ProductVendorListSerializer,
    ReviewSerializer,
    SizeAddSerializer,
    SizeSerializer,
    SizeUpdateSerializer,
    SpecificationAddSerializer,
    SpecificationSerializer,
    SpecificationUpdateSerializer,
    SummarySerializer,
    VendorSerializer,
)
from userauths.models import Profile
from userauths.permissions import IsVendor
from userauths.serializer import ProfileSerializer
from vendor.serializer import ProductCreateSerializer, ProductDetailSerializer

# Create your views here.
from .models import Vendor

# Create your views here.



class DashboardStatsAPIView(generics.ListAPIView):
    serializer_class = SummarySerializer
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated, IsVendor]

    def get_queryset(self):
       

        #calculate summary value
        user = self.request.user

        product_count = Product.objects.filter(vendor__user=user).count()
        order_count = CartOrder.objects.filter(Q(payment_status='paid')|Q(payment_status='cash'),vendor__user=user).count()
        revenue = CartOrderItem.objects.filter(Q(order__payment_status='paid')|Q(order__payment_status='cash'),vendor__user=user, ).aggregate(total_revenue=models.Sum(models.F('sub_total') + models.F('shipping_amount')))['total_revenue'] or 0


        return [{
            'products': product_count,
            'orders':order_count,
            'revenue': revenue,
        }]
    

    def list(self,*args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)



@api_view(('GET',))
def MonthlyOrderChartAPIView(request, vendor_id):
    vendor = Vendor.objects.get(id=vendor_id)
    orders = CartOrder.objects.filter(vendor=vendor, payment_status='paid')
    orders_by_month = orders.annotate(month=ExtractMonth("date")).values("month").annotate(orders=models.Count("id")).order_by("month")
    return Response(orders_by_month)


@api_view(('GET',))
def MonthlyProductChartAPIView(request, vendor_id):
    vendor = Vendor.objects.get(id=vendor_id)
    products = Product.objects.filter(vendor=vendor)
    products_by_month = products.annotate(month=ExtractMonth("date")).values("month").annotate(products=models.Count("id")).order_by("month")
    return Response(products_by_month)



class ProductsAPIView(generics.ListAPIView):
    serializer_class = ProductVendorListSerializer
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated, IsVendor]

    def get_queryset(self):
        products = Product.objects.select_related('category').filter(vendor__user=self.request.user)
        return products
    
    

class OrdersAPIView(generics.ListAPIView):
    serializer_class = CartOrderVendorAllOrdersSerializer
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated, IsVendor]


    def get_queryset(self):
        orders = CartOrder.objects.prefetch_related(Prefetch('orderitem',to_attr='prefetech_orderitem')).filter(Q(payment_status='cash') | Q(payment_status='paid'),vendor__user=self.request.user)
        return orders
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context 
    
    



class OrderDetailAPIView(generics.ListAPIView):
    serializer_class = CartOrderItemVendorSerializer
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated, IsVendor]

    def get_queryset(self):
        order_oid = self.kwargs['order_oid']
        self.order = CartOrder.objects.get(vendor__user=self.request.user, oid=order_oid)
        querset = CartOrderItem.objects.select_related('product','product__category','vendor').prefetch_related('coupon').filter(order=self.order)
        
        return querset

    
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        context['queryset'] = self.get_queryset()
        return context 
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        
        totals = queryset.aggregate(
            subtotal=Sum(F('sub_total')),
            total=Sum(F('total')),
            shipping_amount=Sum(F('shipping_amount')),
            service_fee=Sum(F('service_fee')),
            tax_fee=Sum(F('tax_fee')),
            initial_total=Sum(F('initial_total')),
            saved=Sum(F('saved')),
        )

        # Serialize queryset and combined_totals
        serializer = self.get_serializer(queryset, many=True)
        combined_totals_serializer = CombinedTotalsSerializer(totals)

        # Create response data
        data = {
            'orderitem': serializer.data,
            'vendor_total': combined_totals_serializer.data,
            'order_status': self.order.order_status
        }

        return Response(data)





class RevenueAPIView(generics.ListAPIView):
    serializer_class = CartOrderItemSerializer
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated, IsVendor]

    def get_queryset(self):
        revenue = CartOrderItem.objects.filter(vendor__user=self.request.user, order__payment_status="paid").aggregate(
            total_revenue=models.Sum(models.F('sub_total') + models.F('shipping_amount')))['total_revenue'] or 0
        return revenue
    



class FilterProductsAPIView(generics.ListAPIView):
    serializer_class =ProductVendorListSerializer #ProductSerializer
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated, IsVendor]

    def get_queryset(self):
        filter = self.request.GET.get("filter")
        if filter == "published":
            products = Product.objects.filter(vendor__user=self.request.user, status="published")
        elif filter == "in_review":  
            products = Product.objects.filter(vendor__user=self.request.user, status="in_review")
        elif filter == "draft":  
            products = Product.objects.filter(vendor__user=self.request.user, status="draft")  
        elif filter == "disabled":  
            products = Product.objects.filter(vendor__user=self.request.user, status="disabled")
        else:
            products = Product.objects.filter(vendor__user=self.request.user)
        return products

class EarningAPIView(generics.ListAPIView):
    serializer_class= EarningSerializer
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated, IsVendor]  

    def get_queryset(self):
        one_month_ago = datetime.today() - timedelta(days=28)
        monthly_revenue = CartOrderItem.objects.filter(vendor__user=self.request.user, order__payment_status="paid", date__gte=one_month_ago).aggregate(total_revenue=models.Sum(models.F('sub_total') + models.F('shipping_amount')))['total_revenue'] or 0
        total_revenue = CartOrderItem.objects.filter(vendor__user=self.request.user, order__payment_status="paid").aggregate(total_revenue=models.Sum(models.F('sub_total') + models.F('shipping_amount')))['total_revenue'] or 0

        return[{
            'monthly_revenue':monthly_revenue,
            'total_revenue':total_revenue,
             
         }]
    
    def list(self,*args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)
    

@api_view(('GET',))
def MonthlyEarningTracker(request, vendor_id):
    vendor = Vendor.objects.get(id=vendor_id)
    monthly_earning_tracker = (
        CartOrderItem.objects
        .filter(vendor=vendor, order__payment_status="paid")
        .annotate(
            month=ExtractMonth("date")
        )
        .values("month")
        .annotate(
            sales_count=models.Sum("qty"),
            total_earning=models.Sum(
                models.F('sub_total') + models.F('shipping_amount'))
        )
        .order_by("-month")
    )
    return Response(monthly_earning_tracker)



class ReviewsListAPIView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated, IsVendor]

    def get_queryset(self):
        reviews = Review.objects.filter(product__vendor__user=self.request.user)
        return reviews



class ReviewsDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ReviewSerializer
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated, IsVendor]

    def get_object(self):
        review_id = self.kwargs['review_id']
        review = Review.objects.get(product__vendor__user=self.request.user, id=review_id)
        return review



class CouponListAPIView(generics.ListAPIView):
    serializer_class = CouponSerializer
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated, IsVendor] 

    def get_queryset(self):
        coupon = Coupon.objects.filter(vendor__user=self.request.user)
        return coupon


class CouponCreateAPIView(generics.CreateAPIView):
    serializer_class = CouponSerializer
    queryset = Coupon.objects.all()
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated, IsVendor] 

    def create(self, request, *args, **kwargs):
        payload = request.data

        code = payload.get("code")
        discount_type = payload.get("discount_type")   
        discount_value = payload.get("discount_value") 
        usage_limit = payload.get("usage_limit")
        valid_from = payload.get("valid_from")
        valid_to = payload.get("valid_to")
        active = payload.get("active")
        usage_limit = int(usage_limit) if usage_limit not in [None, "", "null"] else None

        vendor = Vendor.objects.get(user=self.request.user)

        coupon = Coupon.objects.create(
            vendor=vendor,
            code=code,
            discount_type=discount_type,
            discount_value=discount_value,
            usage_limit=usage_limit,
            valid_from=valid_from,
            valid_to=valid_to,
            active=(str(active).lower() == "true")
        )

        return Response({"message": _("Coupon Created Successfully.")}, status=status.HTTP_201_CREATED)

class CouponDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CouponSerializer
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated, IsVendor] 

    def get_object(self):
        coupon_id = self.kwargs['coupon_id']
        coupon = Coupon.objects.get(vendor__user=self.request.user, id=coupon_id)
        return coupon


class CouponStats(generics.ListAPIView):
    serializer_class = CouponSummarySerializer
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated, IsVendor] 

    def get_queryset(self):


        total_coupons = Coupon.objects.filter(vendor__user=self.request.user).count()
        active_coupons = Coupon.objects.filter(vendor__user=self.request.user, active=True).count()

        return [{
            'total_coupons': total_coupons,
            'active_coupons': active_coupons,
        }]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class NotificationUnSeenListAPIView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated, IsVendor] 

    def get_queryset(self):
        notifications = Notification.objects.filter(vendor__user=self.request.user, seen=False).order_by('seen')
        return notifications
    
class NotificationSeenListAPIView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated, IsVendor] 

    def get_queryset(self):
        notifications = Notification.objects.filter(vendor__user=self.request.user, seen=True).order_by('seen')
        return notifications
    
class NotificationSummaryAPIView(generics.ListAPIView):
    serializer_class = NotificationSummarySerializer
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated, IsVendor] 

    def get_queryset(self):
    
        un_read_noti = Notification.objects.filter(vendor__user=self.request.user, seen=False).count()
        read_noti = Notification.objects.filter(vendor__user=self.request.user, seen=True).count()
        all_noti = Notification.objects.filter(vendor__user=self.request.user).count()

        return [{
            'un_read_noti': un_read_noti,
            'read_noti': read_noti,
            'all_noti': all_noti,
        }]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    
class NotificationMarkAsSeen(generics.RetrieveUpdateAPIView):
    serializer_class = NotificationSerializer
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated, IsVendor] 

    def get_object(self):
        noti_id = self.kwargs['noti_id']
        notification = Notification.objects.get(vendor__user=self.request.user, id=noti_id)
        notification.seen = True
        notification.save()
        return notification
    




class VendorProfileUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated, IsVendor] 



class ShopUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated, IsVendor]       


class ShopAPIView(generics.RetrieveUpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = VendorSerializer
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated, IsVendor] 

    def get_object(self):
        vendor_slug = self.kwargs['vendor_slug']

        vendor = Vendor.objects.get(slug=vendor_slug)
        return vendor    


class ShopProductsAPIView(generics.ListAPIView):
    serializer_class = ProductSerializer
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated, IsVendor] 

    def get_queryset(self):
        vendor_slug = self.kwargs['vendor_slug']
        vendor = Vendor.objects.get(slug=vendor_slug)
        products = Product.objects.filter(vendor=vendor)
        return products
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['currency_code'] = self.kwargs.get('currency')
        return context 
    


class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductAddSerializer
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated, IsVendor] 

    @transaction.atomic
    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save()
        product_instance = serializer.instance

        specifications_data = []
        colors_data = []
        sizes_data = []
        gallery_data = []
        # Loop through the keys of self.request.data      
        for key, value in self.request.data.items():
            # Example key: specifications[0][title]
            if key.startswith('specifications') and '[title_en]' in  key:
            
                # Extract index from key
                index = key.split('[')[1].split(']')[0]
                
                title_en = self.request.data.get(f'specifications[{index}][title_en]')
                title_ar = self.request.data.get(f'specifications[{index}][title_ar]')
                content_en = self.request.data.get(f'specifications[{index}][content_en]')
                content_ar = self.request.data.get(f'specifications[{index}][content_ar]')


                specifications_data.append(
                    {'title_en': title_en,'title_ar': title_ar, 'content_en': content_en,'content_ar': content_ar})

            # Example key: colors[0][name]
            elif key.startswith('colors') and '[name_en]' in key:
                

                index = key.split('[')[1].split(']')[0]

                name_en = self.request.data.get(f'colors[{index}][name_en]')                
                name_ar = self.request.data.get(f'colors[{index}][name_ar]')
                color_code = self.request.data.get(f'colors[{index}][color_code]')

                colors_data.append({'name_en': name_en, 'name_ar': name_ar, 'color_code': color_code,})

            # Example key: sizes[0][name]
            elif key.startswith('sizes') and '[name_en]' in key:
                # Extract index from key
                index = key.split('[')[1].split(']')[0]

                name_en = self.request.data.get(f'sizes[{index}][name_en]')                
                name_ar = self.request.data.get(f'sizes[{index}][name_ar]')
                price_key = f'sizes[{index}][price]'
                price = self.request.data.get(price_key)
                sizes_data.append({'name_en': name_en, 'name_ar': name_ar, 'price': price})

            # Example key: gallery[0][image]
            elif key.startswith('gallery') and '[image]' in key:
                # Extract index from key
                index = key.split('[')[1].split(']')[0]
                image = value
                gallery_data.append({'image': image})

        # Log or print the data for debugging
        

        # Save nested serializers with the product instance
        self.save_nested_data(
            product_instance, SpecificationAddSerializer, specifications_data)
        self.save_nested_data(product_instance, ColorAddSerializer, colors_data)
        self.save_nested_data(product_instance, SizeAddSerializer, sizes_data)
        self.save_nested_data(
            product_instance, GallerySerializer, gallery_data)

    def save_nested_data(self, product_instance, serializer_class, data):
        serializer = serializer_class(data=data, many=True, context={
                                      'product_instance': product_instance})
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product_instance)








class ProductUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated, IsVendor] 

    def get_object(self):
        product_pid = self.kwargs['product_pid']
        product = Product.objects.get(vendor__user=self.request.user, pid=product_pid)
        return product

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        product = self.get_object()

        # Deserialize product data
        serializer = self.get_serializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Delete all existing nested data
        
        product.specification().delete()
        product.color().delete()
        product.size().delete()
        product.gallery().delete()

        

        specifications_data = []
        colors_data = []
        sizes_data = []
        gallery_data = []
        # Loop through the keys of self.request.data
        for key, value in self.request.data.items():
            # Example key: specifications[0][title]
            if key.startswith('specifications') and '[title_en]' in  key:
            
                # Extract index from key
                index = key.split('[')[1].split(']')[0]
                
                title_en = self.request.data.get(f'specifications[{index}][title_en]')
                title_ar = self.request.data.get(f'specifications[{index}][title_ar]')
                content_en = self.request.data.get(f'specifications[{index}][content_en]')
                content_ar = self.request.data.get(f'specifications[{index}][content_ar]')


                specifications_data.append(
                    {'title_en': title_en,'title_ar': title_ar, 'content_en': content_en,'content_ar': content_ar})

            # Example key: colors[0][name]
            elif key.startswith('colors') and '[name_en]' in key:
                

                index = key.split('[')[1].split(']')[0]

                name_en = self.request.data.get(f'colors[{index}][name_en]')                
                name_ar = self.request.data.get(f'colors[{index}][name_ar]')
                color_code = self.request.data.get(f'colors[{index}][color_code]')

                colors_data.append({'name_en': name_en, 'name_ar': name_ar, 'color_code': color_code,})

            # Example key: sizes[0][name]
            elif key.startswith('sizes') and '[name_en]' in key:
                # Extract index from key
                index = key.split('[')[1].split(']')[0]

                name_en = self.request.data.get(f'sizes[{index}][name_en]')                
                name_ar = self.request.data.get(f'sizes[{index}][name_ar]')
                price_key = f'sizes[{index}][price]'
                price = self.request.data.get(price_key)
                sizes_data.append({'name_en': name_en, 'name_ar': name_ar, 'price': price})

            # Example key: gallery[0][image]
            elif key.startswith('gallery') and '[image]' in key:
                # Extract index from key
                index = key.split('[')[1].split(']')[0]
                image = value
                gallery_data.append({'image': image})

        # Log or print the data for debugging
        

        # Save nested serializers with the product instance
        self.save_nested_data(
            product, SpecificationSerializer, specifications_data)
        self.save_nested_data(product, ColorSerializer, colors_data)
        self.save_nested_data(product, SizeSerializer, sizes_data)
        self.save_nested_data(product, GallerySerializer, gallery_data)

        return Response({'message': _('Product Updated')}, status=status.HTTP_200_OK)

    def save_nested_data(self, product_instance, serializer_class, data):
        serializer = serializer_class(data=data, many=True, context={
                                      'product_instance': product_instance})
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product_instance)










class ProductDeleteView(generics.DestroyAPIView):
    serializer_class =ProductVendorListSerializer 
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated, IsVendor] 

    def get_queryset(self):
        products = Product.objects.filter(vendor__user=self.request.user)
        return products
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_object(self):
        product_pid = self.kwargs['product_pid']
        product = Product.objects.get(pid=product_pid, vendor__user=self.request.user)
        return product
    def get_complete_image_url(self, image_path):
        # Assuming BASE_URL is defined in your Django settings
        if isinstance(settings.BASE_URL, tuple):
            # Convert tuple to string
            base_url = ''.join(settings.BASE_URL)
        else:
            base_url = settings.BASE_URL
        return base_url + image_path
    

    def get_stats_data(self):
        stats_view = DashboardStatsAPIView()
        stats_view.kwargs = {'vendor_id': self.kwargs['vendor_id']}
        stats_view.request = self.request
        stats_view.format_kwarg = None
        stats_view.format = self.format_kwarg
        stats_view.check_permissions(stats_view.request)
        stats_view.check_object_permissions(stats_view.request, None)
        queryset = stats_view.get_queryset()
        stats_view.list(self.request)
        serializer = stats_view.get_serializer(queryset, many=True)
        return serializer.data[0]
    

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        # Fetch dashboard statistics
        
        stats_data = self.get_stats_data()




        
        queryset = self.get_queryset()  
        serializer = self.serializer_class(queryset, many=True,context={'request': request}).data 

        for item in serializer:
                item['image'] = self.get_complete_image_url(item['image'])
                #item['category']['image'] = self.get_complete_image_url(item['category']['image'])


       


        return Response({
            "status": "Success",
            "message": _("Product deleted successfully"),
            "dashboard_stats": stats_data,
            "products": serializer,
            
           
        }, status=status.HTTP_200_OK)







class ProductDetailUpdate(generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductAddSerializer
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated, IsVendor] 

    def get_object(self):
        product_pid = self.kwargs['product_pid']        
        product = Product.objects.get(vendor__user=self.request.user, pid=product_pid)
        return product

    def update(self, request, *args, **kwargs):
        product = self.get_object()

        # Deserialize product data
        serializer = self.get_serializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product)
        updated_product_serializer = self.get_serializer(product)

        return Response({
            'message': _('Product details have been updated successfully'),
            'product': updated_product_serializer.data
        }, status=status.HTTP_200_OK)












class GalleryUpdateView(generics.UpdateAPIView):
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated, IsVendor] 

    def get_object(self):
        product_pid = self.kwargs['product_pid']
        gallery_gid = self.request.data.get('gallery_gid')

        product = Product.objects.get(vendor__user=self.request.user, pid=product_pid)
       
        if gallery_gid:
            try:
                gallery = Gallery.objects.get(product=product, gid=gallery_gid)
                return gallery
            except Gallery.DoesNotExist:
                raise ValidationError("Gallery matching query does not exist.")
        else:
            # If gallery_gid is None, create a new gallery
            gallery_data = {'product': product.pk, 'image': self.request.data.get('image'), "active": self.request.data.get('active') }  # Assuming 'image' is provided in request data
            serializer = GallerySerializer(data=gallery_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return serializer.instance
        
    # def get_complete_image_url(self, image_path):
    #     # Assuming BASE_URL is defined in your Django settings
    #     if isinstance(settings.BASE_URL, tuple):
    #         # Convert tuple to string
    #         base_url = ''.join(settings.BASE_URL)
    #     else:
    #         base_url = settings.BASE_URL
    #     return base_url + image_path

    # def get_complete_image_url(self, image_path):
    #     # Assuming BASE_URL is defined in your Django settings
    #     base_url = settings.BASE_URL
    #     if isinstance(base_url, tuple):
    #         # Convert tuple to string
    #         base_url = ''.join(base_url)
    #     complete_url = urljoin(base_url, image_path)
    #    return complete_url


    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Deserialize gallery data
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'message': _('Gallery details have been updated successfully'),'gallery' : serializer.data}, status=status.HTTP_200_OK)


        # Retrieve all galleries for the product

        # product = instance.product
        # galleries = Gallery.objects.filter(product=product)
        
        # for gallery in galleries:
        #     gallery.image = self.get_complete_image_url(gallery.image.url)
        # gallery_serializer = GallerySerializer(galleries, many=True)

        #return Response({'message': _('Gallery details have been updated successfully'),'galleries' : gallery_serializer.data}, status=status.HTTP_200_OK)


    


class ColorUpdateView(generics.UpdateAPIView):
    queryset = Color.objects.all()
    serializer_class = ColorUpdateSerializer
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated, IsVendor] 

    def get_object(self):
        product_pid = self.kwargs['product_pid']
        color_cid = self.request.data.get('color_cid')

        product = Product.objects.get(vendor__user=self.request.user, pid=product_pid)
       
        if color_cid:
            try:
                color = Color.objects.get(product=product, cid=color_cid)
                return color
            except Color.DoesNotExist:
                raise ValidationError("Color matching query does not exist.")
        else:
            # If gallery_gid is None, create a new gallery
            color_data = {'product': product.pk, 'name_en': self.request.data.get('name_en'),'name_ar': self.request.data.get('name_ar'), "color_code": self.request.data.get('color_code') }  # Assuming 'image' is provided in request data
            serializer = ColorUpdateSerializer(data=color_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return serializer.instance


    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Deserialize gallery data
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'message': _('Color have been updated successfully'),'colors' : serializer.data}, status=status.HTTP_200_OK)

    


class SpecificationUpdateView(generics.UpdateAPIView):
    queryset = Specification.objects.all()
    serializer_class = SpecificationUpdateSerializer
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated, IsVendor] 

    def get_object(self):
        product_pid = self.kwargs['product_pid']
        spid = self.request.data.get('spid')
        product = Product.objects.get(vendor__user=self.request.user, pid=product_pid)
       
        if spid:
            try:
                specification = Specification.objects.get(product=product, spid=spid)
                return specification
            except Specification.DoesNotExist:
                raise ValidationError("Specification matching query does not exist.")
        else:
            # If gallery_gid is None, create a new gallery
            specification = {'product': product.pk, 'title_en': self.request.data.get('title_en'),'title_ar': self.request.data.get('title_ar'), "content_en": self.request.data.get('content_en'),"content_ar": self.request.data.get('content_ar') }  # Assuming 'image' is provided in request data
            serializer = SpecificationUpdateSerializer(data=specification)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return serializer.instance


    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'message': _('Specification have been updated successfully'),'Specification' : serializer.data}, status=status.HTTP_200_OK)



class SizeUpdateView(generics.UpdateAPIView):
    queryset = Size.objects.all()
    serializer_class = SizeUpdateSerializer
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated, IsVendor] 

    def get_object(self):
        product_pid = self.kwargs['product_pid']
        sid = self.request.data.get('sid')

        product = Product.objects.get(vendor__user=self.request.user, pid=product_pid)
       
        if sid:
            try:
                size = Size.objects.get(product=product, sid=sid)
                return size
            except Size.DoesNotExist:
                raise ValidationError("Size matching query does not exist.")
        else:
            # If gallery_gid is None, create a new gallery
            size_data = {'product': product.pk, 'name_en': self.request.data.get('name_en'),'name_ar': self.request.data.get('name_ar')}  # Assuming 'image' is provided in request data
            serializer = SizeUpdateSerializer(data=size_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return serializer.instance


    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Deserialize gallery data
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'message': _('Size have been updated successfully'),'Size' : serializer.data}, status=status.HTTP_200_OK)

    


class SizeDeleteView(generics.DestroyAPIView):
    queryset = Size.objects.all()
    serializer_class = SizeUpdateSerializer
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated, IsVendor] 

    def get_object(self):
        product_pid = self.kwargs['product_pid']
        sid = self.request.data.get('sid')

        product = Product.objects.get(vendor__user=self.request.user, pid=product_pid)               
        size = Size.objects.get(product=product, sid=sid)
        return size

    def get_queryset(self):
        product_pid = self.kwargs['product_pid']
        product = Product.objects.get(vendor__user=self.request.user, pid=product_pid)               
        size = Size.objects.filter(product=product)
        return size
        


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        queryset = self.get_queryset()  
        serializer = self.serializer_class(queryset, many=True).data
  


        return Response({
            "status": "Success",
            "message": _("Size deleted successfully"),
            "sizes": serializer,
            
           
        }, status=status.HTTP_200_OK)   


class ColorDeleteView(generics.DestroyAPIView):
    queryset = Color.objects.all()
    serializer_class = ColorUpdateSerializer
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated, IsVendor] 


    def get_object(self):
        product_pid = self.kwargs['product_pid']
        color_cid = self.request.data.get('color_cid')

        product = Product.objects.get(vendor__user=self.request.user, pid=product_pid)               
        color = Color.objects.get(product=product, cid=color_cid)
        return color
    def get_queryset(self):
        product_pid = self.kwargs['product_pid']
        product = Product.objects.get(vendor__user=self.request.user, pid=product_pid)               
        color = Color.objects.filter(product=product)
        return color
    


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        queryset = self.get_queryset()  
        serializer = self.serializer_class(queryset, many=True).data
  


        return Response({
            "status": "Success",
            "message": _("Color deleted successfully"),
            "sizes": serializer,
            
           
        }, status=status.HTTP_200_OK)   
                


class SpecificationDeleteView(generics.DestroyAPIView):
    queryset = Specification.objects.all()
    serializer_class = SpecificationUpdateSerializer
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated, IsVendor] 


    def get_object(self):
        product_pid = self.kwargs['product_pid']
        spid = self.request.data.get('spid')
        product = Product.objects.get(vendor__user=self.request.user, pid=product_pid)               
        specification = Specification.objects.get(product=product, spid=spid)
        return specification
    def get_queryset(self):
        product_pid = self.kwargs['product_pid']
        product = Product.objects.get(vendor__user=self.request.user, pid=product_pid)               
        specification = Specification.objects.filter(product=product)
        return specification
    


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        queryset = self.get_queryset()  
        serializer = self.serializer_class(queryset, many=True).data
  


        return Response({
            "status": "Success",
            "message": _("Specification deleted successfully"),
            "sizes": serializer,
            
           
        }, status=status.HTTP_200_OK)   
                

        

class GalleryDeleteView(generics.DestroyAPIView):
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated, IsVendor] 


    def get_object(self):
        product_pid = self.kwargs['product_pid']
        gallery_gid = self.request.data.get('gallery_gid')
        product = Product.objects.get(vendor__user=self.request.user, pid=product_pid)               
        gallery = Gallery.objects.get(product=product, gid=gallery_gid)
        return gallery
    def get_queryset(self):
        product_pid = self.kwargs['product_pid']
        product = Product.objects.get(vendor__user=self.request.user, pid=product_pid)               
        gallery = Gallery.objects.filter(product=product)
        return gallery
    
    def get_complete_image_path(self, image_path):
        return self.request.build_absolute_uri(image_path)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        queryset = self.get_queryset()  
        serializer = self.serializer_class(queryset, many=True).data

        for item in serializer:
            item['image'] = self.get_complete_image_path(item['image'])
  


        return Response({
            "status": "Success",
            "message": _("Gallery deleted successfully"),
            "sizes": serializer,
            
           
        }, status=status.HTTP_200_OK)   
                

class ChangeOrderStatusView(generics.UpdateAPIView):
    serializer_class = ChangeOrderStatusSerializer
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated, IsVendor]

    def get_object(self):
        order_oid = self.kwargs['order_oid']
        user_id = self.request.user
        order = CartOrder.objects.get(oid=order_oid, vendor__user=user_id)
        return order

        
class NewCreateProduct(generics.CreateAPIView,generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductCreateSerializer
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated, IsVendor]
    lookup_field='pid'

    def get_serializer_context(self):
        user_inst = self.request.user
        context = super().get_serializer_context()
        context['user_inst'] = user_inst
        return context

        
        
        

        