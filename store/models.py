from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.


class Color(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='products/')
    colors = models.ManyToManyField(Color) 
    description = models.TextField()
    
    
    def __str__(self):
        return self.name

class ProductSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="sizes")  # Link to Product
    size = models.CharField(max_length=50)  # e.g., 4oz, 6oz, 8oz
    price = models.IntegerField()


    def __str__(self):
        return f"{self.product.name} - {self.size}"




class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15,  blank=True, null=True)
    email = models.EmailField( blank=True, null=True)
    address = models.TextField()
    total_price = models.IntegerField(default=0)
    cart_details = models.TextField(null=True, blank=True)  # Stores the cart items as a text field
    created_at = models.DateTimeField(auto_now_add=True)  # This will automatically store the date of creation
    # items = models.ManyToManyField(Cart) 


    def __str__(self):
        return f"Order {self.user} - {self.total_price}- {self.phone_number}-{self.email}"

    def __str__(self):
        phone_number = self.phone_number if self.phone_number else "No Phone"
        email = self.email if self.email else "No Email"
        return f"Order {self.user} - {self.total_price} - {phone_number} - {email}"
    

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    size = models.ForeignKey(ProductSize, on_delete=models.CASCADE, default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    color = models.CharField(max_length=20, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.product.name} - {self.size.size} ({self.quantity})"

    def total_price(self):
        return self.size.price * self.quantity


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return f"Message from {self.name} - {self.email}"
    


class CartHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    size = models.ForeignKey(ProductSize, on_delete=models.SET_NULL, null=True, blank=True)
    color = models.CharField(max_length=20)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)  # <-- Add this


    def __str__(self):
        return f"{self.user.username} - {self.product.name} (x{self.quantity})"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s review on {self.product.name}"
    

