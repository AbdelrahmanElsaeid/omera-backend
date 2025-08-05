from django.db import models
from django.utils.text import slugify
from userauths.models import User
# Create your models here.


class Vendor(models.Model):
    name_en = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100,null=True, blank=True)
    description_en = models.TextField(null=True, blank=True)
    description_ar = models.TextField(null=True, blank=True)
    user= models.OneToOneField(User, on_delete=models.CASCADE)
    image= models.ImageField(upload_to='vendor', blank=True, null=True, default="vendor.jpg" )
    #name = models.CharField(max_length=100, help_text="Shop Name", null=True,blank=True)
    email = models.CharField(max_length=1000, null=True,blank=True)
    #description = models.TextField(null=True,blank=True)
    mobile=models.CharField(max_length=100, help_text="Shop Mobile Number", null=True, blank=True)
    activate = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    slug=models.SlugField(unique=True, max_length=500)


    class Meta:
        verbose_name_plural = "Vendors"
        ordering = ['date']

   
    def __str__(self):
        if self.name_en:
            return str(self.name_en)
        if self.name_ar:
            return str(self.name_ar)

    def save(self,*args, **kwargs):
        if self.slug == "" or self.slug== None:
            self.slug =slugify(self.name_en)

        super(Vendor, self).save(*args, **kwargs)        