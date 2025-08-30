from decimal import Decimal
from rest_framework import serializers
from django.utils.translation import get_language
from userauths.serializer import ProfileReviewSerializer
from .models import (
    Product,
    Category,
    Brand,
    Gallery,
    Specification,
    Color,
    Size,
    Cart,
    CartOrder,
    CartOrderItem,
    Coupon,
    ProductFaq,
    Review,
    Wishlist,
    Notification,
)
from vendor.models import Vendor


class BrandSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        exclude = ["title_en", "title_ar"]

    def get_title(self, obj):
        request = self.context.get("request")
        language = request.LANGUAGE_CODE if request else "en"
        if language == "ar":
            return obj.title_ar
        return obj.title_en


class CategorySerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()

    class Meta:
        model = Category
        exclude = ["title_en", "title_ar"]

    def get_title(self, obj):
        request = self.context.get("request")
        language = request.LANGUAGE_CODE if request else "en"
        if language == "ar":
            return obj.title_ar
        return obj.title_en


class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = "__all__"


class SpecificationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = "__all__"


class SizeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = "__all__"


class ColorUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = "__all__"


class SpecificationSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()

    class Meta:
        model = Specification
        fields = ["id", "title", "content"]

    def get_title(self, obj):
        request = self.context.get("request")
        language = request.LANGUAGE_CODE if request else "en"
        if language == "ar":
            return obj.title_ar
        return obj.title_en

    def get_content(self, obj):
        request = self.context.get("request")
        language = request.LANGUAGE_CODE if request else "en"
        if language == "ar":
            return obj.content_ar
        return obj.content_en


class SizeSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Size
        exclude = ["name_en", "name_ar"]

    def get_name(self, obj):
        request = self.context.get("request")
        language = request.LANGUAGE_CODE if request else "en"
        if language == "ar":
            return obj.name_ar
        return obj.name_en


class ColorSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Color
        exclude = ["name_en", "name_ar"]

    def get_name(self, obj):
        request = self.context.get("request")
        language = request.LANGUAGE_CODE if request else "en"
        if language == "ar":
            return obj.name_ar
        return obj.name_en


class ProductListSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()

    price = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "image",
            "price",
            "currency",
            "views",
            "rating",
            "category",
            "brand",
            
            "slug",
        ]

    def get_price(self, obj):
        currency_code = self.context.get("currency_code")
        if currency_code == "EGP":
            return obj.price_EGP
        elif currency_code == "AED":
            return obj.price_AED
        else:
            return None

    def get_currency(self, obj):
        currency_code = self.context.get("currency_code")
        if currency_code == "EGP":
            return "EGP"
        elif currency_code == "AED":
            return "AED"
        else:
            return None

    def get_title(self, obj):
        request = self.context.get("request")
        language = request.LANGUAGE_CODE if request else "en"
        if language == "ar":
            return obj.title_ar
        return obj.title_en

    def get_category(self, obj):
        request = self.context.get("request")
        language = request.LANGUAGE_CODE if request else "en"
        if language == "ar":
            return obj.category.title_ar if obj.category else None
        return obj.category.title_en if obj.category else None

    def get_brand(self, obj):
        request = self.context.get("request")
        language = request.LANGUAGE_CODE if request else "en"
        if language == "ar":
            return obj.brand.title_ar if obj.brand else None
        return obj.brand.title_en if obj.brand else None


class ProductDetailSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    gallery = GallerySerializer(many=True)
    color = ColorSerializer(many=True)
    size = SizeSerializer(many=True)
    specification = SpecificationSerializer(many=True)
    vendor = serializers.StringRelatedField()
    price = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "image",
            "description",
            "category",
            "brand",
            "price",
            "currency",
            "old_price",
            "shipping_amount",
            "stock_qty",
            "in_stock",
            "status",
            "featured",
            "views",
            "rating",
            "vendor",
            "pid",
            "slug",
            "date",
            "gallery",
            "specification",
            "size",
            "color",
            "product_rating",
            "rating_count",
        ]
    def get_price(self, obj):
        currency_code = self.context.get("currency_code")
        if currency_code == "EGP":
            return obj.price_EGP
        elif currency_code == "AED":
            return obj.price_AED
        else:
            return None

    def get_currency(self, obj):
        currency_code = self.context.get("currency_code")
        if currency_code == "EGP":
            return "EGP"
        elif currency_code == "AED":
            return "AED"
        else:
            return None

    def get_title(self, obj):
        request = self.context.get("request")
        language = request.LANGUAGE_CODE if request else "en"
        if language == "ar":
            return obj.title_ar
        return obj.title_en

    def get_description(self, obj):
        request = self.context.get("request")
        language = request.LANGUAGE_CODE if request else "en"
        if language == "ar":
            return obj.description_ar
        return obj.description_en

    def get_category(self, obj):
        request = self.context.get("request")
        language = request.LANGUAGE_CODE if request else "en"
        if language == "ar":
            return obj.category.title_ar if obj.category else None
        return obj.category.title_en if obj.category else None

    def get_brand(self, obj):
        request = self.context.get("request")
        language = request.LANGUAGE_CODE if request else "en"
        if language == "ar":
            return obj.brand.title_ar if obj.brand else None
        return obj.brand.title_en if obj.brand else None

    def __init__(self, *args, **kwargs):
        super(ProductDetailSerializer, self).__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.method == "POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 3


class ProductFaqSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFaq
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(ProductFaqSerializer, self).__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.method == "POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 3


class CartSerializer(serializers.ModelSerializer):
    product = ProductListSerializer()

    class Meta:
        model = Cart
        fields = "__all__"


class CartOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartOrderItem
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(CartOrderItemSerializer, self).__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.method == "POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 3


class CartOrderSerializer(serializers.ModelSerializer):
    orderitem = CartOrderItemSerializer(many=True, read_only=True)
    payment_status = serializers.CharField(source="get_payment_status_display")
    order_status = serializers.CharField(source="get_order_status_display")

    class Meta:
        model = CartOrder
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(CartOrderSerializer, self).__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.method == "POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 3

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")

        # Translate product title if available
        for item in data["orderitem"]:
            # Translate category name if available
            if "product" in item and "category" in item["product"]:
                category = item["product"]["category"]
                if request:
                    lang_code = request.LANGUAGE_CODE
                    if lang_code == "ar" and "title_ar" in category:
                        category["title"] = category["title_ar"]
                    elif lang_code == "en" and "title_en" in category:
                        category["title"] = category["title_en"]
                    category.pop("title_en")
                    category.pop("title_ar")

            # Translate brand name if available
            if "product" in item and "brand" in item["product"]:
                brand = item["product"]["brand"]
                if request:
                    lang_code = request.LANGUAGE_CODE
                    if lang_code == "ar" and "title_ar" in brand:
                        brand["title"] = brand["title_ar"]
                    elif lang_code == "en" and "title_en" in brand:
                        brand["title"] = brand["title_en"]
                    brand.pop("title_en")
                    brand.pop("title_ar")

            # Translate product title and description if available
            if "product" in item:
                product = item["product"]
                if request:
                    lang_code = request.LANGUAGE_CODE
                    if lang_code == "ar" and "title_ar" in product:
                        product["title"] = product["title_ar"]
                    elif lang_code == "en" and "title_en" in product:
                        product["title"] = product["title_en"]

                    product.pop("title_en")
                    product.pop("title_ar")
                    if lang_code == "ar" and "description_ar" in product:
                        product["description"] = product["description_ar"]
                    elif lang_code == "en" and "description_en" in product:
                        product["description"] = product["description_en"]

                    product.pop("description_ar")
                    product.pop("description_en")

        return data


class VendorSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = Vendor
        exclude = ["name_en", "name_ar", "description_en", "description_ar"]

    def get_name(self, obj):
        request = self.context.get("request")
        language = request.LANGUAGE_CODE if request else "en"
        if language == "ar":
            return obj.name_ar
        return obj.name_en

    def get_description(self, obj):
        request = self.context.get("request")
        language = request.LANGUAGE_CODE if request else "en"
        if language == "ar":
            return obj.description_ar
        return obj.description_en

    def __init__(self, *args, **kwargs):
        super(VendorSerializer, self).__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.method == "POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 3


from django.conf import settings


class ReviewSerializer(serializers.ModelSerializer):
    profile = ProfileReviewSerializer()

    class Meta:
        model = Review
        fields = ["id", "profile", "review", "rating", "date"]

   


class WishlistSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField()
    user = serializers.StringRelatedField()

    class Meta:
        model = Wishlist
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(WishlistSerializer, self).__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.method == "POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 3


class WishlistListSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Wishlist
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(WishlistListSerializer, self).__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.method == "POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 3

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        product_representation = representation.pop("product")
        currency_code = self.context.get("currency_code")

        # Check the language
        language = get_language()

        # Set the title based on the language
        if language == "ar" and "title_ar" in product_representation:
            title = product_representation["title_ar"]
        elif language == "en" and "title_en" in product_representation:
            title = product_representation["title_en"]
        else:
            title = None

        if language == "ar" and "description_ar" in product_representation:
            description = product_representation["description_ar"]
        elif language == "en" and "description_en" in product_representation:
            description = product_representation["description_en"]
        else:
            description = None

        if title is not None:
            # representation['title'] = title
            product_representation["title"] = title

        if description is not None:
            product_representation["description"] = description

        # Check if converted_price exists in the product representation
        if "price" in product_representation:
            representation["price"] = product_representation["price"]

        if currency_code == "EGP":
            price = product_representation.get("price_EGP")
        elif currency_code == "AED":
            price = product_representation.get("price_AED")
        else:
            price = None

        # Set converted_price to price based on currency code
        if price is not None:
            product_representation["price"] = Decimal(price)
        else:
            product_representation["price"] = None
        # product_representation['price'] = Decimal(price)
        product_representation["currency"] = currency_code

        # Remove price_EGP and price_AED fields
        product_representation.pop("price_EGP", None)
        product_representation.pop("price_AED", None)

        # Remove desc and title fields
        product_representation.pop("title_en", None)
        product_representation.pop("title_ar", None)
        product_representation.pop("description_en", None)
        product_representation.pop("description_ar", None)

        representation["product"] = product_representation
        return representation


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = "__all__"


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(NotificationSerializer, self).__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.method == "POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 3


class ReviewSummarySerializer(serializers.Serializer):
    one_star = serializers.IntegerField(default=0)
    two_star = serializers.IntegerField(default=0)
    three_star = serializers.IntegerField(default=0)
    four_star = serializers.IntegerField(default=0)
    five_star = serializers.IntegerField(default=0)


################################


class SummarySerializer(serializers.Serializer):
    products = serializers.IntegerField()
    orders = serializers.IntegerField()
    revenue = serializers.DecimalField(max_digits=12, decimal_places=2)


class EarningSerializer(serializers.Serializer):
    monthly_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)


class CouponSummarySerializer(serializers.Serializer):
    total_coupons = serializers.IntegerField(default=0)
    active_coupons = serializers.IntegerField(default=0)


class NotificationSummarySerializer(serializers.Serializer):
    un_read_noti = serializers.IntegerField(default=0)
    read_noti = serializers.IntegerField(default=0)
    all_noti = serializers.IntegerField(default=0)


class ProductSerializer(serializers.ModelSerializer):
    gallery = GallerySerializer(many=True, required=False)
    color = ColorSerializer(many=True, required=False)
    size = SizeSerializer(many=True, required=False)
    specification = SpecificationSerializer(many=True, required=False)
    # prices = PriceSerializer(many=True,required=False)

    class Meta:
        model = Product
        fields = [
            "id",
            "title_en",
            "title_ar",
            "image",
            "description_en",
            "description_ar",
            "category",
            "price_EGP",
            "price_AED",
            # "prices",
            "old_price",
            "shipping_amount",
            "stock_qty",
            "in_stock",
            "status",
            "featured",
            "views",
            "rating",
            "vendor",
            "pid",
            "slug",
            "date",
            "gallery",
            "specification",
            "size",
            "color",
            "product_rating",
            "rating_count",
            "orders",
        ]

    def __init__(self, *args, **kwargs):
        super(ProductSerializer, self).__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.method == "POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 3


class SizeAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = "__all__"


class SpecificationAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = "__all__"


class ColorAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = "__all__"


class ProductAddSerializer(serializers.ModelSerializer):
    gallery = GallerySerializer(many=True, required=False, read_only=True)
    color = ColorAddSerializer(many=True, required=False)
    size = SizeAddSerializer(many=True, required=False)
    specification = SpecificationAddSerializer(many=True, required=False)
    # prices = PriceSerializer(many=True,required=False)
    # image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "title_en",
            "title_ar",
            "image",
            "description_en",
            "description_ar",
            "category",
            "brand",
            "price_EGP",
            "price_AED",
            # "prices",
            "old_price",
            # "shipping_amount",
            "stock_qty",
            "in_stock",
            "status",
            "featured",
            "views",
            # "rating",
            "vendor",
            "pid",
            "slug",
            "date",
            "gallery",
            "specification",
            "size",
            "color",
            "product_rating",
            "rating_count",
            "orders",
            "sku",
            "is_new",
        ]

    # def get_image(self, instance):
    #     request = self.context.get('request')
    #     if instance.image:
    #         return request.build_absolute_uri(instance.image.url)
    #     return None

    def __init__(self, *args, **kwargs):
        super(ProductAddSerializer, self).__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.method == "POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 3


class Gallery2Serializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = "__all__"


class Specification2Serializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = "__all__"


class Size2Serializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = "__all__"


class Color2Serializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = "__all__"


class Product2Serializer(serializers.ModelSerializer):
    galleries = Gallery2Serializer(many=True, required=False)
    specifications = Specification2Serializer(many=True, required=False)
    sizes = Size2Serializer(many=True, required=False)
    colors = Color2Serializer(many=True, required=False)

    class Meta:
        model = Product
        fields = "__all__"

    def create(self, validated_data):
        galleries_data = validated_data.pop("galleries", [])
        specifications_data = validated_data.pop("specifications", [])
        sizes_data = validated_data.pop("sizes", [])
        colors_data = validated_data.pop("colors", [])

        product = Product.objects.create(**validated_data)

        for gallery_data in galleries_data:
            Gallery.objects.create(product=product, **gallery_data)

        for specification_data in specifications_data:
            Specification.objects.create(product=product, **specification_data)

        for size_data in sizes_data:
            Size.objects.create(product=product, **size_data)

        for color_data in colors_data:
            Color.objects.create(product=product, **color_data)

        return product


class ProductVendorListSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "title_en",
            "image",
            "category",
            "price_EGP",
            "stock_qty",
            "in_stock",
            "status",
            "rating",
            "pid",
            "slug",
            "orders",
            "sku"
        ]

    def get_category(self, obj):
        return obj.category.title_en if obj.category else None


class ProductOrderSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ("id", "title_en", "image", "price_EGP", "category",'sku')

    def get_category(self, obj):
        """get category"""
        return obj.category.title_en


class VendorOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ("id", "name_en", "email", "mobile", "address")


class CartOrderItemVendorSerializer(serializers.ModelSerializer):
    product = ProductOrderSerializer()
    vendor = VendorOrderSerializer()

    class Meta:
        model = CartOrderItem
        fields = "__all__"

    # def __init__(self, *args, **kwargs):
    #     super(CartOrderItemVendorSerializer, self).__init__(*args, **kwargs)
    #     request = self.context.get('request')
    #     if request and request.method == 'POST':
    #         self.Meta.depth = 0
    #     else:
    #         self.Meta.depth = 3

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)

    #     # Access request from serializer context
    #     request = self.context.get('request')
    #     queryset = self.context.get('queryset')

    #     if request:
    #         # Translate product title and description if available
    #         if 'product' in representation:
    #             product = representation['product']
    #             lang_code = request.LANGUAGE_CODE

    #             if lang_code == 'ar' and 'title_ar' in product:
    #                 product['title'] = product['title_ar']
    #             elif lang_code == 'en' and 'title_en' in product:
    #                 product['title'] = product['title_en']

    #             product.pop('title_en', None)
    #             product.pop('title_ar', None)

    #             if lang_code == 'ar' and 'description_ar' in product:
    #                 product['description'] = product['description_ar']
    #             elif lang_code == 'en' and 'description_en' in product:
    #                 product['description'] = product['description_en']

    #             product.pop('description_ar', None)
    #             product.pop('description_en', None)

    #             # Translate category title
    #             if 'category' in product:
    #                 category = product['category']

    #                 if lang_code == 'ar' and 'title_ar' in category:
    #                     category['title'] = category['title_ar']
    #                 elif lang_code == 'en' and 'title_en' in category:
    #                     category['title'] = category['title_en']

    #                 category.pop('title_en', None)
    #                 category.pop('title_ar', None)

    #             # Translate brand name
    #             if 'brand' in product:
    #                 brand = product['brand']

    #                 if lang_code == 'ar' and 'title_ar' in brand:
    #                     brand['title'] = brand['title_ar']
    #                 elif lang_code == 'en' and 'title_en' in brand:
    #                     brand['title'] = brand['title_en']

    #                 brand.pop('title_en', None)
    #                 brand.pop('title_ar', None)

    #     return representation


class CombinedTotalsSerializer(serializers.Serializer):
    subtotal = serializers.FloatField()
    total = serializers.FloatField()
    shipping_amount = serializers.FloatField()
    service_fee = serializers.FloatField()
    tax_fee = serializers.FloatField()
    initial_total = serializers.FloatField()
    saved = serializers.FloatField()


class CartOrderVendorAllOrdersSerializer(serializers.ModelSerializer):
    # orderitem = CartOrderItemSerializer(many=True, read_only=True)
    payment_status = serializers.CharField(source="get_payment_status_display")
    order_status = serializers.CharField(source="get_order_status_display")
    vendor_total = serializers.SerializerMethodField()

    class Meta:
        model = CartOrder
        fields = (
            "id",
            "payment_status",
            "order_status",
            "vendor_total",
            "date",
            "full_name",
            "oid",
        )

    # def __init__(self, *args, **kwargs):
    #     super(CartOrderVendorAllOrdersSerializer, self).__init__(*args, **kwargs)
    #     request = self.context.get('request')
    #     if request and request.method == 'POST':
    #         self.Meta.depth = 0
    #     else:
    #         self.Meta.depth = 3

    def get_vendor_total(self, instance):
        """
        Calculate and return the total amount for the specific vendor in the order.
        """
        order_items = getattr(instance, "prefetech_orderitem", [])

        # vendor_id = self.context.get('vendor_id')  # Get vendor_id from serializer context
        # order_items = instance.orderitem.all()  # Get all order items for the order

        vendor_total = sum(
            item.total for item in order_items
        )  # Calculate total for the specific vendor
        return vendor_total

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     request = self.context.get('request')

    #     # Translate product title if available
    #     for item in data['orderitem']:
    #     # Translate category name if available
    #         if 'product' in item and 'category' in item['product']:
    #             category = item['product']['category']
    #             if request:
    #                 lang_code = request.LANGUAGE_CODE
    #                 if lang_code == 'ar' and 'title_ar' in category:
    #                     category['title'] = category['title_ar']
    #                 elif lang_code == 'en' and 'title_en' in category:
    #                     category['title'] = category['title_en']
    #                 category.pop('title_en')
    #                 category.pop('title_ar')

    #         # Translate brand name if available
    #         if 'product' in item and 'brand' in item['product']:
    #             brand = item['product']['brand']
    #             if request:
    #                 lang_code = request.LANGUAGE_CODE
    #                 if lang_code == 'ar' and 'title_ar' in brand:
    #                     brand['title'] = brand['title_ar']
    #                 elif lang_code == 'en' and 'title_en' in brand:
    #                     brand['title'] = brand['title_en']
    #                 brand.pop('title_en')
    #                 brand.pop('title_ar')

    #         # Translate product title and description if available
    #         if 'product' in item:
    #             product = item['product']
    #             if request:
    #                 lang_code = request.LANGUAGE_CODE
    #                 if lang_code == 'ar' and 'title_ar' in product:
    #                     product['title'] = product['title_ar']
    #                 elif lang_code == 'en' and 'title_en' in product:
    #                     product['title'] = product['title_en']

    #                 product.pop('title_en')
    #                 product.pop('title_ar')
    #                 if lang_code == 'ar' and 'description_ar' in product:
    #                     product['description'] = product['description_ar']
    #                 elif lang_code == 'en' and 'description_en' in product:
    #                     product['description'] = product['description_en']

    #                 product.pop('description_ar')
    #                 product.pop('description_en')

    #     return data


class ChangeOrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartOrder
        fields = ['order_status']