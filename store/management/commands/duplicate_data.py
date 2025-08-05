from django.core.management.base import BaseCommand
from store.models import Product, Gallery, Specification, Size, Color
from faker import Faker
import random
from django.utils.crypto import get_random_string

fake = Faker()

# class Command(BaseCommand):
#     help = 'Duplicate data with fake titles'

#     def generate_fake_title(self):
#         return fake.text(max_nb_chars=50)  # Generate a fake title

#     def duplicate_product_and_related(self, product_instance):
#         new_title = self.generate_fake_title()  # Generate a new fake title
#         # Duplicate Product instance
#         new_pid = get_random_string(length=10)
#         product_instance.pk = None  # Create a new instance
#         product_instance.title = new_title  # Set the new fake title
#         product_instance.slug = None
#         product_instance.pid = new_pid
#         product_instance.save()

#         # Duplicate related Gallery instances
#         galleries = Gallery.objects.filter(product=product_instance)
#         for gallery in galleries:
#             gallery.pk = None
#             gallery.product = product_instance
            
#             gallery.save()

#         # Duplicate related Specification instances
#         specifications = Specification.objects.filter(product=product_instance)
#         for specification in specifications:
#             specification.pk = None
#             specification.product = product_instance
#             specification.save()

#         # Duplicate related Size instances
#         sizes = Size.objects.filter(product=product_instance)
#         for size in sizes:
#             size.pk = None
#             size.product = product_instance
#             size.save()

#         # Duplicate related Color instances
#         colors = Color.objects.filter(product=product_instance)
#         for color in colors:
#             color.pk = None
#             color.product = product_instance
#             color.save()

#     def handle(self, *args, **kwargs):
#         products = Product.objects.all()
#         for product in products:
#             self.duplicate_product_and_related(product)
#         self.stdout.write(self.style.SUCCESS('Data duplicated successfully with fake titles.'))

class Command(BaseCommand):
    help = 'Duplicate data with fake titles'

    def generate_fake_title(self):
        return fake.text(max_nb_chars=50)  # Generate a fake title

    def duplicate_product_and_related(self, product_instance):
        new_title = self.generate_fake_title()  # Generate a new fake title
        
        # Duplicate Product instance
        product_instance.pk = None  # Create a new instance
        product_instance.title = new_title  # Set the new fake title
        product_instance.slug = None
        product_instance.pid = get_random_string(length=10)  # Generate a new unique pid
        product_instance.save()

        # Duplicate related Gallery instances
        galleries = product_instance.gallery_set.all()
        for gallery in galleries:
            gallery.pk = None
            gallery.product_id = None  # Clear the product foreign key to avoid integrity error
            gallery.save()

        # Duplicate related Specification instances
        specifications = product_instance.specification_set.all()
        for specification in specifications:
            specification.pk = None
            specification.product_id = None  # Clear the product foreign key
            specification.save()

        # Duplicate related Size instances
        sizes = product_instance.size_product.all()
        for size in sizes:
            size.pk = None
            size.product_id = None  # Clear the product foreign key
            size.save()

        # Duplicate related Color instances
        colors = product_instance.color_product.all()
        for color in colors:
            color.pk = None
            color.product_id = None  # Clear the product foreign key
            color.save()

    def handle(self, *args, **kwargs):
        products = Product.objects.all()
        for product in products:
            self.duplicate_product_and_related(product)
        self.stdout.write(self.style.SUCCESS('Data duplicated successfully with fake titles.'))
