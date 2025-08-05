# myapp/management/commands/update_product_translations.py

from django.core.management.base import BaseCommand
from store.models import Product,Specification,Size,Color,Brand,Category

class Command(BaseCommand):
    help = 'Update product translations'

    def handle(self, *args, **kwargs):
        # products = Product.objects.all()
        # for product in products:
        #     if not product.title_en:
        #         product.title_en = product.title
        #     if not product.description_en:
        #         product.description_en = product.description
        #     product.save()
        # self.stdout.write(self.style.SUCCESS('Successfully updated product translations'))

        # specifications = Specification.objects.all()
        # for sp in specifications:
        #     if not sp.title_en:
        #         sp.title_en = sp.title
        #     if not sp.content_en:
        #         sp.content_en = sp.content
        #     sp.save()
        # self.stdout.write(self.style.SUCCESS('Successfully updated specification translations'))

        # sizes = Size.objects.all()
        # for siz in sizes:
        #     if not siz.name_en:
        #         siz.name_en = siz.name
            
        #     siz.save()
        # self.stdout.write(self.style.SUCCESS('Successfully updated size translations'))

        # colors = Color.objects.all()
        # for color in colors:
        #     if not color.name_en:
        #         color.name_en = color.name
            
        #     color.save()
        # self.stdout.write(self.style.SUCCESS('Successfully updated color translations'))

        brands = Brand.objects.all()
        for br in brands:
            if not br.title_en:
                br.title_en = br.title
            
            br.save()
        self.stdout.write(self.style.SUCCESS('Successfully updated brand translations'))

        categories = Category.objects.all()
        for ca in categories:
            if not ca.title_en:
                ca.title_en = ca.title
            
            ca.save()
        self.stdout.write(self.style.SUCCESS('Successfully updated category translations'))
