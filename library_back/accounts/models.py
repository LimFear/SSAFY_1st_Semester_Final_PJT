from django.db import models
from django.contrib.auth.models import AbstractUser
from articles.models import Category

# Create your models here.
class User(AbstractUser):
    categories = models.ManyToManyField(Category)
    
    def __str__(self):
        return self.username