from django.db import models
from django.contrib.auth.models import AbstractUser
from articles.models import Category

# Create your models here.
class User(AbstractUser):
    # category = models.ForeignKey(Category, on_delete=models.CASCADE)
    pass