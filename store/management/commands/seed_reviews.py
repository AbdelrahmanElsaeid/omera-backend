# management/commands/seed_reviews.py

from django.core.management.base import BaseCommand
from faker import Faker
import random
from store.models import Product, Review
from userauths.models import User

class Command(BaseCommand):
    help = 'Seed product reviews'

    def handle(self, *args, **kwargs):
        ids = [2,3,4,5,6,7,8,9,10,11,12,13,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,57,58,59]

        fake = Faker()
        for i in ids:
            try:
                product = Product.objects.get(id=i)
            except Product.DoesNotExist:
                continue

            Review.objects.create(
                product=product,
                review=fake.text(),
                rating=random.randint(1, 5),
                user=User.objects.get(id=random.randint(1, 6))
            )

        self.stdout.write(self.style.SUCCESS(f"{len(ids)} Product Review(s) Seeded"))
