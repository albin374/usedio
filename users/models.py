from django.contrib.auth.models import User
# models.py
from django.db import models
from django.db import models
from django.contrib.auth.models import User

    
class Category(models.Model):
    cat_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='product_images/')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    sold = models.BooleanField(default=False)  # Add this line to track if the product is sold
    purchased_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='purchased_products')



    def __str__(self):
        return f"{self.name} ({self.model})"

from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(default=now)
    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Shipped', 'Shipped'),
            ('Delivered', 'Delivered'),
            ('Cancelled', 'Cancelled')
        ],
        default='Pending'
    )

    def __str__(self):
        return f"Order {self.order_id} - {self.product.name} by {self.buyer.username}"



