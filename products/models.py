from django.db import models
from django.contrib.auth import get_user_model
from django.forms import ValidationError
from django.contrib.auth.models import User
# Get the user model, supporting custom user models
users = get_user_model()

class Product(models.Model):
    PAYMENT_CHOICES = [
        ('per week', 'Per Week'),
        ('per month', 'Per Month'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    pay_every = models.CharField(
        max_length=15,
        choices=PAYMENT_CHOICES,
        default='per week'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.IntegerField()
    image = models.ImageField(upload_to="", null=True, blank=True)
    

    def clean(self):
        if self.price < 0.00:
            raise ValidationError("Price cannot be negative.")
        if self.stock <= 0:
            raise ValidationError("Stock cannot be negative.")
        
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    in_cart = models.BooleanField(default=False)    

    def __str__(self):
        return f"{self.quantity} {self.product.name} in {self.user.username}'s cart"
