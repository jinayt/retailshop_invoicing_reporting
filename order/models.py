from django.db import models
from django.contrib.auth.models import User

class Client(models.Model):
    client_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    gender = models.CharField(max_length=1,default='')
    date_of_birth = models.DateField(null=True)
    mobile = models.CharField(max_length=10)
    email = models.EmailField()
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255)
    line3 = models.CharField(max_length=255)
    city = models.CharField(max_length=150)
    state = models.CharField(max_length=150)
    pincode = models.CharField(max_length=6)
    last_update = models.DateTimeField(auto_now=True)

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    client_id = models.ForeignKey(Client, on_delete=models.CASCADE)
    order_date = models.DateField()
    last_update = models.DateTimeField(auto_now=True)
    
class OrderItems(models.Model):
    item_id = models.AutoField(primary_key = True)
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=14, decimal_places=2)
    rate = models.DecimalField(max_digits=14, decimal_places=2)
    units = models.CharField(max_length=20,null=True)
    truck_number = models.CharField(max_length=20, null=True)
    weight = models.ImageField(upload_to='image/', null=True, blank=True)
    last_update = models.DateTimeField(auto_now=True)
   
class Payment(models.Model):
    tran_id = models.AutoField(primary_key = True)
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    status = models.CharField(max_length=2)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    roundoff = models.DecimalField(max_digits=14, decimal_places=2)
    last_update = models.DateTimeField(auto_now=True)