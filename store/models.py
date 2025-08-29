from django.db import models
from userauths.models import Profile, User
from vendor.models import Vendor
from shortuuid.django_fields import ShortUUIDField
from django.utils.text import slugify
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save
from unidecode import unidecode
import shortuuid
import uuid
from django.utils.translation import gettext_lazy as _


# Create your models here.
def generate_default_uid():
    # Use _create_uuid() method of ShortUUIDField to generate a UUID
    default_uid = str(uuid.uuid4())[:10]

    return default_uid




class Brand(models.Model):
    title_en = models.CharField(max_length=100)
    title_ar = models.CharField(max_length=100,null=True, blank=True)
    #title = models.CharField(max_length=100)
    image = models.FileField(upload_to="brand", default="brand.jpg", null=True, blank=True)    
    slug = models.SlugField(unique=True)

    def __str__(self):
        if self.title_en:
            return self.title_en
        if self.title_ar:
            return self.title_ar

class Category(models.Model):
    title_en = models.CharField(max_length=100)
    title_ar = models.CharField(max_length=100,null=True, blank=True)
    #title = models.CharField(max_length=100)
    image = models.FileField(upload_to="category", default="category.jpg", null=True, blank=True)
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        if self.title_en:
            return self.title_en
        if self.title_ar:
            return self.title_ar
    
    class Meta:
        verbose_name_plural="Category"
        #ordering = ['title']

class Product(models.Model):

    STATUS = (
        ("draft","draft"),
        ("disabled","disabled"),
        ("in_review","in_review"),
        ("published","published"),
    )
    title_en = models.CharField(max_length=100)
    title_ar = models.CharField(max_length=100,null=True, blank=True)
    description_en = models.TextField(null=True, blank=True)
    description_ar = models.TextField(null=True, blank=True)
    image = models.FileField(upload_to="product",default="product.jpg", null=True, blank=True)
    category= models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    brand= models.ForeignKey(Brand, on_delete=models.CASCADE, null=True, blank=True)
    price_EGP = models.DecimalField(decimal_places=2, max_digits=12, default=0.00 , null=True, blank=True)
    price_AED = models.DecimalField(decimal_places=2, max_digits=12, default=0.00, null=True, blank=True)
    old_price = models.DecimalField(decimal_places=2, max_digits=12, default=0.00, null=True, blank=True)
    shipping_amount = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    stock_qty = models.PositiveIntegerField(default=1)
    in_stock = models.BooleanField(default=True)
    status = models.CharField(max_length=100, choices=STATUS, default="published")
    featured = models.BooleanField(default=False)
    views= models.PositiveIntegerField(default=0)
    rating = models.PositiveIntegerField(default=0,null=True, blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    pid = ShortUUIDField(unique=True, length=10, alphabet="abcdefg123456")
    slug = models.SlugField(unique=True,null=True,blank=True)
    date = models.DateTimeField(auto_now_add=True)
    sku = models.CharField(max_length=100, null=True, blank=True)
    is_new = models.BooleanField(default=False)

 

    def __str__(self):
        if self.title_en:
            return self.title_en
        if self.title_ar:
            return self.title_ar
    
    def product_rating(self):
        product_rating = Review.objects.filter(product=self).aggregate(avg_rating=models.Avg("rating"))
        return product_rating['avg_rating']
    
    def rating_count(self):
        return Review.objects.filter(product=self).count()
    
    def gallery(self):
        return Gallery.objects.filter(product=self)
    def specification(self):
        return Specification.objects.filter(product=self)
    def color(self):
        return Color.objects.filter(product=self)
    def size(self):
        return Size.objects.filter(product=self)
    def orders(self):
        return CartOrderItem.objects.filter(product=self).count()
    
   

    def save(self, *args, **kwargs):
        # Generate slug from English title if available
        uuid_key = shortuuid.uuid()
        uniqueid = uuid_key[:4]

        if self.title_en and not self.slug:
            self.slug = slugify(self.title_en) + "-" + str(uniqueid.lower())
        # If English title is not available, generate slug from Arabic title
        elif self.title_ar and not self.slug:
            self.slug = slugify(unidecode(self.title_ar)) + "-" + str(uniqueid.lower())

        # if self.title_en and (not self.slug or self.title_en != self.title_ar):
        #     self.slug = slugify(self.title_en)+ "-" + str(uniqueid.lower())
        # # If English title is not available, generate slug from Arabic title
        # elif self.title_ar and (not self.slug or self.title_ar != self.title_en):
        #    self.slug = slugify(unidecode(self.title_ar))+ "-" + str(uniqueid.lower())

        # Calculate rating
        self.rating = self.product_rating()
        if self.stock_qty is not None:
            if self.stock_qty == 0:
                self.in_stock = False
                
            if self.stock_qty > 0:
                self.in_stock = True
        else:
            self.stock_qty = 0
            self.in_stock = False
        super(Product, self).save(*args, **kwargs)    



class Gallery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    image = models.FileField(upload_to="products",default="product.jpg")
    active = models.BooleanField(default=True)
    date=models.DateTimeField(auto_now_add=True)
    gid=ShortUUIDField(unique=True, length=10,alphabet="abcdefg123456")

    class Meta:
        verbose_name_plural="Product Images"

    def __str__(self):
        if self.product.title_en:
            return self.product.title_en
        if self.product.title_ar:
            return self.product.title_ar
    

class Specification(models.Model):
    title_en = models.CharField(max_length=100,null=True, blank=True)
    title_ar = models.CharField(max_length=100,null=True, blank=True)
    content_en = models.TextField(null=True, blank=True)
    content_ar = models.TextField(null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    #title = models.CharField(max_length=1000)
    #content=models.CharField(max_length=1000)
    date=models.DateTimeField(auto_now_add=True)
    spid=ShortUUIDField(length=10,alphabet="abcdefg123456", null=True, blank=True)

    def __str__(self):
        if self.title_en:
            return self.title_en
        if self.title_ar:
            return self.title_ar
        else:
            return "spe"


class Size(models.Model):
    name_en = models.CharField(max_length=100,null=True, blank=True)
    name_ar = models.CharField(max_length=100,null=True, blank=True)
    product = models.ForeignKey(Product,related_name="size_product", on_delete=models.SET_NULL, null=True)
    #name = models.CharField(max_length=1000)
    price = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    date=models.DateTimeField(auto_now_add=True)
    sid=ShortUUIDField(length=10,alphabet="abcdefg123456",null=True, blank=True)


    def __str__(self):
        if self.name_en:
            return self.name_en
        if self.name_ar:
            return self.name_ar
        else:
            return "size"
   


class Color(models.Model):
    product = models.ForeignKey(Product,related_name="color_product", on_delete=models.SET_NULL, null=True)
    #name = models.CharField(max_length=1000)
    color_code = models.CharField(max_length=1000,null=True, blank=True)
    name_en = models.CharField(max_length=100,null=True, blank=True)
    name_ar = models.CharField(max_length=100,null=True, blank=True)
    cid=ShortUUIDField(length=10,alphabet="abcdefg123456",null=True, blank=True)


    def __str__(self):
        if self.name_en:
            return self.name_en
        if self.name_ar:
            return self.name_ar
        else:
            return "color"
   



class Cart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    qty = models.PositiveIntegerField(default=0, null=True, blank=True)
    price = models.DecimalField(decimal_places=2, max_digits=12, default=0.00, null=True, blank=True)
    currency = models.CharField(max_length=50, null=True, blank=True)
    sub_total = models.DecimalField(decimal_places=2, max_digits=12, default=0.00, null=True, blank=True)
    shipping_amount = models.DecimalField(decimal_places=2, max_digits=12, default=0.00, null=True, blank=True)
    service_fee = models.DecimalField(decimal_places=2, max_digits=12, default=0.00, null=True, blank=True)
    tax_fee = models.DecimalField(decimal_places=2, max_digits=12, default=0.00, null=True, blank=True)
    total = models.DecimalField(decimal_places=2, max_digits=12, default=0.00, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)
    cart_id = models.CharField(max_length=1000, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.product.title_en:
            return f'{self.cart_id} - {self.product.title_en}'
        if self.product.title_ar:
            return f'{self.cart_id} - {self.product.title_ar}'
    




class CartOrder(models.Model):
    # PAYMENT_STATUS = (
    # ("paid", "Paid"),
    # ("pending", "Pending"),
    # ("processing", "Processing"),
    # ("cancelled", "Cancelled"),
    # ("initiated", 'Initiated'),
    # ("failed", 'failed'),
    # ("refunding", 'refunding'),
    # ("refunded", 'refunded'),
    # ("unpaid", 'unpaid'),
    # ("expired", 'expired'),
    # )


    # ORDER_STATUS = (
    #     ("Pending", "Pending"),
    #     ("Fulfilled", "Fulfilled"),
    #     ("Partially Fulfilled", "Partially Fulfilled"),
    #     ("Cancelled", "Cancelled"),
        
    #)
    PAYMENT_STATUS = (
        ("paid", _("Paid")),
        ("pending", _("Pending")),
        ("processing", _("Processing")),
        ("cancelled", _("Cancelled")),
        ("initiated", _('Initiated')),
        ("failed", _('Failed')),
        ("refunding", _('Refunding')),
        ("refunded", _('Refunded')),
        ("unpaid", _('Unpaid')),
        ("expired", _('Expired')),
        ("cash", _('Cash')),
    )

    ORDER_STATUS = (
        ("Pending", _("Pending")),
        ("Fulfilled", _("Fulfilled")),
        ("Partially Fulfilled", _("Partially Fulfilled")),
        ("Delivered", _("Delivered")),
        ("Approved", _("Approved")),
        ("On Delivery", _("On Delivery")),
        ("Cancelled", _("Cancelled")),
    )
    vendor = models.ManyToManyField(Vendor, blank=True)
    buyer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="buyer", blank=True)
    sub_total = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    shipping_amount = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    tax_fee = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    service_fee = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    total = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    payment_status = models.CharField(max_length=100, choices=PAYMENT_STATUS, default="initiated")
    order_status = models.CharField(max_length=100, choices=ORDER_STATUS, default="Pending")
    initial_total = models.DecimalField(default=0.00, max_digits=12, decimal_places=2, help_text="The original total before discounts")
    saved = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True, help_text="Amount saved by customer")
    full_name = models.CharField(max_length=1000)
    email = models.CharField(max_length=1000,blank=True, null=True)
    mobile = models.CharField(max_length=1000)
    address = models.CharField(max_length=1000, null=True, blank=True)
    city = models.CharField(max_length=1000, null=True, blank=True)
    state = models.CharField(max_length=1000, null=True, blank=True)
    country = models.CharField(max_length=1000, null=True, blank=True)
    currency = models.CharField(max_length=50, null=True, blank=True)

    stripe_session_id = models.CharField(max_length=1000, null=True, blank=True)
    cart_order_id = models.CharField(max_length=1000, null=True, blank=True)

    
    oid = ShortUUIDField(length=10, max_length=25, alphabet="abcdefghijklmnopqrstuvxyz")
    date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Cart Order"

    def __str__(self):
        return self.oid
    
    def get_payment_status_display(self):
        return dict(self.PAYMENT_STATUS)[self.payment_status]

    def get_order_status_display(self):
        return dict(self.ORDER_STATUS)[self.order_status]
    
    def orderitem(self):
        return CartOrderItem.objects.filter(order=self)





class CartOrderItem(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE, related_name="orderitem")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="order_item")
    qty = models.IntegerField(default=0)
    color = models.CharField(max_length=100, null=True, blank=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=1000, null=True, blank=True)

    sub_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Total of Product price * Product Qty")
    shipping_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Estimated Shipping Fee = shipping_fee * total")
    tax_fee = models.DecimalField(default=0.00, max_digits=12, decimal_places=2, help_text="Estimated Vat based on delivery country = tax_rate * (total + shipping)")
    service_fee = models.DecimalField(default=0.00, max_digits=12, decimal_places=2, help_text="Estimated Service Fee = service_fee * total (paid by buyer to platform)")
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Grand Total of all amount listed above")
    initial_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Grand Total of all amount listed above before discount")
    saved = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True, help_text="Amount saved by customer")
    
    coupon = models.ManyToManyField('Coupon', blank=True)
    oid = ShortUUIDField(length=10, max_length=25, alphabet="abcdefghijklmnopqrstuvxyz")
    date = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return self.oid
    
    


class ProductFaq(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    email= models.EmailField(null=True, blank=True)
    question= models.CharField(max_length=1000)
    answer= models.TextField(null=True, blank=True)
    active= models.BooleanField(default=False)    
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question
    class Meta:
        verbose_name_plural = "Product FAQs"


# Define a model for Reviews
class Review(models.Model):
    RATING = (
    ( 1,  "1 Star"),
    ( 2,  "2 Star"),
    ( 3,  "3 Star"),
    ( 4,  "4 Star"),
    ( 5,  "5 Star"),
)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True, related_name="reviews")
    review = models.TextField()
    reply = models.CharField(null=True, blank=True, max_length=1000)
    rating = models.IntegerField(choices=RATING, default=None)
    active = models.BooleanField(default=False)
    helpful = models.ManyToManyField(User, blank=True, related_name="helpful")
    not_helpful = models.ManyToManyField(User, blank=True, related_name="not_helpful")
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Reviews & Rating"
        ordering = ["-date"]
        
    def __str__(self):
        
        if self.product.title_en:
            return self.product.title_en
        if self.product.title_ar:
            return self.product.title_ar
        else:
            return "Review"

    def profile(self):
        return Profile.objects.get(user=self.user)    
   
@receiver(post_save, sender=Review)
def update_product_rating(sender, instance,  **kwargs):
    if instance.product:
        instance.product.save()

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlist")
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Wishlist"
    
    def __str__(self):
        if self.product.title_en:
            return self.product.title_en
        if self.product.title_ar:
            return self.product.title_ar
        else:
            return "Wishlist"
        




class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(CartOrder, on_delete=models.SET_NULL, null=True, blank=True)
    order_item = models.ForeignKey(CartOrderItem, on_delete=models.SET_NULL, null=True, blank=True)
    seen = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Notification"
    
    def __str__(self):
        if self.order:
            return self.order.oid
        else:
            return f"Notification - {self.pk}"
        


class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = (
        ("percent", "Percentage"),
        ("amount", "Fixed Amount"),
    )
    discount_type = models.CharField(
        max_length=10, choices=DISCOUNT_TYPE_CHOICES, default="percent"
    )
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, related_name="coupon_vendor")
    used_by = models.ManyToManyField(User, blank=True)
    code = models.CharField(max_length=50,unique=True)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(null=True, blank=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0,null=True, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
   
    def __str__(self):
        return self.code 
    
    # def is_valid(self, user=None):
    #     """ Check if the coupon is valid for the given user """

    #     now = timezone.now()
    #     if not self.active:
    #         return False
    #     if self.valid_from and now < self.valid_from:
    #         return False
    #     if self.valid_to and now > self.valid_to:
    #         return False
    #     if self.usage_limit and self.used_count >= self.usage_limit:
    #         return False
    #     if user and self.used_by.filter(id=user.id).exists():
    #         return False
    #     return True
    def is_valid(self, user=None):
        """Check if the coupon is valid for the given user, return (bool, reason)."""
        now = timezone.now()

        if not self.active:
            return False, "Coupon is not active"
        if self.valid_from and now < self.valid_from:
            return False, "Coupon is not yet valid"
        if self.valid_to and now > self.valid_to:
            return False, "Coupon has expired"
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False, "Coupon usage limit reached"
        if user and self.used_by.filter(id=user.id).exists():
            return False, "You have already used this coupon"

        return True, "Coupon is valid"

    
    
    def apply_discount(self, total):
        """ Apply the discount to the given total """
        if self.discount_type == "percent":
            discount = (total * self.discount_value) / 100
        else:
            discount = self.discount_value
        return max(total - discount, 0)     
    


class Tax(models.Model):
    country = models.CharField(max_length=100)
    rate = models.IntegerField(default=5, help_text='Number added here are in precentage e.g 5%')
    active = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.country

    class Meta:
        verbose_name_plural = "Taxes"
        ordering = ['country']  