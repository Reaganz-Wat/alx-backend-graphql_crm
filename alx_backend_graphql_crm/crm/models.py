from django.db import models

# Create your models here.
class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="orders")
    products = models.ManyToManyField(Product, related_name="orders")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    order_date = models.DateTimeField(auto_now_add=True)

    def calculate_total(self):
        total = sum(product.price for product in self.products.all())
        self.total_amount = total
        self.save()
        return total

    def __str__(self):
        return f"Order #{self.id} by {self.customer.name}"
