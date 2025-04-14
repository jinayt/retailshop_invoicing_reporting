from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # user_role = models.CharField( max_length=1)
    mobile_no = models.TextField(max_length=10)   