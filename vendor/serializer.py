import json
from rest_framework import serializers

from store.models import Brand, Category, Color, Gallery, Product, Size, Specification
from vendor.models import Vendor


class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ["image"]


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ["name_en", "name_ar", "color_code"]


class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = ["title_en", "title_ar", "content_en", "content_ar"]


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ["name_en", "name_ar"]


class ProductCreateSerializer(serializers.ModelSerializer):
    # These fields are for writing data from the FormData request
    image = serializers.FileField(write_only=True, required=False)
    gallery = serializers.ListField(
        child=serializers.FileField(), write_only=True, required=False
    )
    colors = serializers.JSONField(write_only=True, required=False)
    specifications = serializers.JSONField(write_only=True, required=False)
    sizes = serializers.JSONField(write_only=True, required=False)
    gallery_gid = serializers.JSONField(write_only=True, required=False)

    class Meta:
        model = Product
        fields = [
            "title_en",
            "description_en",
            "image",
            "category",
            "brand",
            "price_EGP",
            "stock_qty",
            "sku",
            "is_new",
            "gallery",
            "colors",
            "specifications",
            "sizes",
            "gallery_gid",
        ]

    def create(self, validated_data):
        # Pop all nested data and files
        gallery_files = validated_data.pop("gallery", [])
        colors_data = validated_data.pop("colors", "[]")
        specifications_data = validated_data.pop("specifications", "[]")
        sizes_data = validated_data.pop("sizes", "[]")

        user_inst = self.context["user_inst"]
        vendor = Vendor.objects.get(user=user_inst)
        validated_data["vendor"] = vendor


        # Create the Product instance first
        product = Product.objects.create(**validated_data)

        # Create nested objects and link them to the new product
        for file in gallery_files:
            Gallery.objects.create(product=product, image=file)

        for color in colors_data:
            Color.objects.create(product=product, **color)

        for spec in specifications_data:
            Specification.objects.create(product=product, **spec)

        for size in sizes_data:
            Size.objects.create(product=product, **size)

        return product
    

    def update(self, instance, validated_data):
        # Pop nested data
        gallery_files = validated_data.pop("gallery", [])
        colors_data = validated_data.pop("colors", [])
        specifications_data = validated_data.pop("specifications", [])
        sizes_data = validated_data.pop("sizes", [])
        gallery_gid = validated_data.pop("gallery_gid", [])

        # Update main product fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # ✅ Gallery: add new images

        if gallery_files:
            if gallery_gid:
                ids = [int(i) for i in gallery_gid]
                instance.gallery_set.exclude(id__in=ids).delete()

            for g in gallery_files:
                Gallery.objects.create(product=instance, image=g)
        elif not gallery_files and gallery_gid:
            ids = [int(i) for i in gallery_gid]
            instance.gallery_set.exclude(id__in=ids).delete()
        else:
            instance.gallery_set.all().delete()

        # ✅ Colors: simple approach — delete all then recreate
        if colors_data:
            instance.color_product.all().delete()
            for color in colors_data:
                Color.objects.create(product=instance, **color)

        # ✅ Specifications
        if specifications_data:
            instance.specification_set.all().delete()
            for spec in specifications_data:
                Specification.objects.create(product=instance, **spec)

        # ✅ Sizes
        if sizes_data:
            instance.size_product.all().delete()
            for size in sizes_data:
                Size.objects.create(product=instance, **size)

        return instance


class GalleryAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = "__all__"


class SpecificationAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = "__all__"


class SizeAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = "__all__"


class ColorAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = "__all__"


class BrandSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="title_en")

    class Meta:
        model = Brand
        fields = ("id", "name")


class CategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="title_en")

    class Meta:
        model = Category
        fields = ("id", "name")


class ProductDetailSerializer(serializers.ModelSerializer):
    gallery = GalleryAllSerializer(many=True, required=False, read_only=True)
    color = ColorAddSerializer(many=True, required=False)
    size = SizeAddSerializer(many=True, required=False)
    specification = SpecificationAddSerializer(many=True, required=False)
    category = CategorySerializer(required=False)
    brand = BrandSerializer(required=False)

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
            "old_price",
            "stock_qty",
            "in_stock",
            "status",
            "featured",
            "views",
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
