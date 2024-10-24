from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Product


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name','price', 'get_image', "stock")

    def get_image(self, obj):
        if obj.image:  # Correctly reference the image field
            return mark_safe(f'<img src="{obj.image.url}" style="width: 50px; height: auto;" />')
        return "No Image"
    get_image.short_description = 'Image'
    
class OffersAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount')

admin.site.register(Product, ProductAdmin)
