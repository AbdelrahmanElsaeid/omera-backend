from django.urls import path

from userauths import views as userauths_views
from rest_framework_simplejwt.views import TokenRefreshView
from store import views as store_views
from customer import views as customer_views
from vendor import views as vendor_views
from store.paymob_payment import PaymobPaymentView, PaymobCallbackView

urlpatterns = [
    path('user/token/', userauths_views.MyTokenOptainPairView.as_view()),
    path('user/token/refresh/', TokenRefreshView.as_view()),
    path('user/register/', userauths_views.RegisterView.as_view()),
    path('user/password-reset/', userauths_views.PasswordRestEmailVerify.as_view()),
    path('user/password-change/', userauths_views.PasswordChangeView.as_view()),
    path('user/profile/<user_id>/', userauths_views.ProfileView.as_view()),

    path('user/login/', userauths_views.LoginView.as_view()),
    path('user/csr/', userauths_views.get_csrf_token),


    # Store Endpoint
    path('productss/<currency>/', store_views.Fpro.as_view()),




    path('category/', store_views.CategoryListAPIView.as_view()),
    path('brand/', store_views.BrandListAPIView.as_view()),
    path('product/<currency>/', store_views.ProductListAPIView.as_view()),
    path('product/<currency>/<slug:slug>/', store_views.ProductDetailAPIView.as_view()),
    path('product/category/<currency>/<str:category>/',store_views.ProductCategory.as_view()),
    path('reviews/',store_views.ReviewListAPIView.as_view()),
    path('reviews/<product_id>/',store_views.ReviewListAPIView.as_view()),
    #path('reviews/summary/<product_id>/',store_views.ReviewSummaryAPIView.as_view()), 

    path('product/brand/<currency>/<str:brand>/',store_views.ProductBrandListAPIView.as_view()),
    path('product-popular/<currency>/',store_views.PopularProductsAPIView.as_view()),
    path('product-bestseller/<currency>/',store_views.BestSellerProductsAPIView.as_view()),
    
    path('products/create/', store_views.ProductCreateAPIView.as_view()),
    path('products/update/<int:pk>/', store_views.ProductCreateAPIView.as_view()),



    path('cart-view/', store_views.CartAPIView.as_view()),
    path('cart-list/<str:cart_id>/<int:user_id>/', store_views.CartListView.as_view()),
    path('cart-list/<str:cart_id>/', store_views.CartListView.as_view()),
    path('cart-detail/<str:cart_id>/<int:user_id>/', store_views.CartDetailView.as_view()),
    path('cart-detail/<str:cart_id>/', store_views.CartDetailView.as_view()),


    path('cart-delete/<str:cart_id>/<int:item_id>/<int:user_id>/',store_views.CartItemDeleteAPIView.as_view()),
    path('cart-delete/<str:cart_id>/<int:item_id>/',store_views.CartItemDeleteAPIView.as_view()),
    path('create-order/',store_views.CreateOrderAPIView.as_view()),
    path('checkout/<order_oid>/',store_views.CheckoutView.as_view()),
    path('coupon/',store_views.CouponAPIView.as_view()),

    #payments
    path('stripe-checkout/<order_oid>/<cart_id>/',store_views.StripeCheckoutView.as_view()),
    path('payment-success/<order_oid>/',store_views.PaymentSuccessView.as_view()),

    #paymob payment

    path('paymob-test/<order_oid>/<payment_method>/', PaymobPaymentView.as_view(), name='paymob'),    
    path('paymob/callback/', PaymobCallbackView.as_view(), name='paymob_payment_success'),


    #Customer Endpoint
    path('customer/orders/<user_id>/',customer_views.OrderAPIView.as_view()),
    path('customer/orders/<user_id>/<order_oid>/',customer_views.OrderDetailAPIView.as_view()),
    #path('customer/wishlist/<user_id>/',customer_views.WishListAPIView.as_view()),
    path('customer/wishlist/create/', customer_views.WishlistCreateAPIView.as_view(), name='customer-wishlist-create'),
    path('customer/wishlist/<currency>/<user_id>/', customer_views.WishlistAPIView.as_view(), name='customer-wishlist'),
    path('customer/notifications/<user_id>/',customer_views.NotificationListAPIView.as_view()),
    path('customer/notifications/<user_id>/<noti_id>/',customer_views.MarkCustomerNotificationAsSeen.as_view()),

    #vendor Dashboard

    path('vendor/stats/<vendor_id>/', vendor_views.DashboardStatsAPIView.as_view()),
    path('vendor-orders-chart/<vendor_id>/', vendor_views.MonthlyOrderChartAPIView),
    path('vendor-products-chart/<vendor_id>/', vendor_views.MonthlyProductChartAPIView),
    path('vendor/products/<vendor_id>/', vendor_views.ProductsAPIView.as_view(), name='vendor-prdoucts'),
    path('vendor/orders/<vendor_id>/', vendor_views.OrdersAPIView.as_view(), name='vendor-orders'),
    path('vendor/orders/<vendor_id>/<order_oid>/', vendor_views.OrderDetailAPIView.as_view(), name='vendor-order-detail'),
    path('vendor/revenue/<vendor_id>/', vendor_views.RevenueAPIView.as_view(), name='vendor-orders'),
    path('vendor-product-filter/<vendor_id>', vendor_views.FilterProductsAPIView.as_view(), name='vendor-product-filter'),
    path('vendor-earning/<vendor_id>/', vendor_views.EarningAPIView.as_view(), name='vendor-product-filter'),
    path('vendor-monthly-earning/<vendor_id>/', vendor_views.MonthlyEarningTracker, name='vendor-product-filter'),
    path('vendor-reviews/<vendor_id>/', vendor_views.ReviewsListAPIView.as_view(), name='vendor-reviews'),
    path('vendor-reviews/<vendor_id>/<review_id>/', vendor_views.ReviewsDetailAPIView.as_view(), name='vendor-review-detail'),
    path('vendor-coupon-list/<vendor_id>/', vendor_views.CouponListAPIView.as_view(), name='vendor-coupon-list'),
    path('vendor-coupon-stats/<vendor_id>/', vendor_views.CouponStats.as_view(), name='vendor-coupon-stats'),
    path('vendor-coupon-detail/<vendor_id>/<coupon_id>/', vendor_views.CouponDetailAPIView.as_view(), name='vendor-coupon-detail'),
    path('vendor-coupon-create/<vendor_id>/', vendor_views.CouponCreateAPIView.as_view(), name='vendor-coupon-create'),
    path('vendor-notifications-unseen/<vendor_id>/', vendor_views.NotificationUnSeenListAPIView.as_view(), name='vendor-notifications-list'),
    path('vendor-notifications-seen/<vendor_id>/', vendor_views.NotificationSeenListAPIView.as_view(), name='vendor-notifications-list'),
    path('vendor-notifications-summary/<vendor_id>/', vendor_views.NotificationSummaryAPIView.as_view(), name='vendor-notifications-summary'),
    path('vendor-notifications-mark-as-seen/<vendor_id>/<noti_id>/', vendor_views.NotificationMarkAsSeen.as_view(), name='vendor-notifications-mark-as-seen'),
    path('vendor-settings/<int:pk>/', vendor_views.VendorProfileUpdateView.as_view(), name='vendor-settings'),
    path('vendor-shop-settings/<int:pk>/', vendor_views.ShopUpdateView.as_view(), name='customer-settings'),
    path('shop/<vendor_slug>/', vendor_views.ShopAPIView.as_view(), name='shop'),
    path('vendor-products/<vendor_slug>/', vendor_views.ShopProductsAPIView.as_view(), name='vendor-products'),
    path('vendor-product-create/', vendor_views.ProductCreateView.as_view(), name='vendor-product-create'),
    path('vendor-product-update/<vendor_id>/<product_pid>/', vendor_views.ProductUpdateView.as_view(), name='vendor-product-update'),
    path('vendor-product-delete/<vendor_id>/<product_pid>/', vendor_views.ProductDeleteView.as_view(), name='vendor-product-delete'),


    path('vendor-productDetail-update/<vendor_id>/<product_pid>/', vendor_views.ProductDetailUpdate.as_view(), name='vendor-product-update'),
    path('vendor-productGallery-update/<vendor_id>/<product_pid>/', vendor_views.GalleryUpdateView.as_view(), name='vendor-product-update'),
    path('vendor-productColor-update/<vendor_id>/<product_pid>/', vendor_views.ColorUpdateView.as_view(), name='vendor-product-update'),
    path('vendor-productSpecification-update/<vendor_id>/<product_pid>/', vendor_views.SpecificationUpdateView.as_view(), name='vendor-product-update'),
    path('vendor-productSize-update/<vendor_id>/<product_pid>/', vendor_views.SizeUpdateView.as_view(), name='vendor-product-update'),


    path('vendor-productGallery-delete/<vendor_id>/<product_pid>/', vendor_views.GalleryDeleteView.as_view(), name='vendor-product-update'),
    path('vendor-productSpecification-delete/<vendor_id>/<product_pid>/', vendor_views.SpecificationDeleteView.as_view(), name='vendor-product-update'),
    path('vendor-productColor-delete/<vendor_id>/<product_pid>/', vendor_views.ColorDeleteView.as_view(), name='vendor-product-update'),
    path('vendor-productSize-delete/<vendor_id>/<product_pid>/', vendor_views.SizeDeleteView.as_view(), name='vendor-product-update'),









]
