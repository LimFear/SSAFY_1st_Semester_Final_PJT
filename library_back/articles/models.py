from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

class Book(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='books')
    title = models.CharField(max_length=200)
    description = models.TextField()
    isbn = models.CharField(max_length=20)
    cover = models.CharField(max_length=300) 
    publisher = models.CharField(max_length=100)
    pub_date = models.DateField()
    author = models.CharField(max_length=100)
    author_info = models.CharField(max_length=500) 
    author_photo = models.CharField(max_length=300)
    customer_review_rank = models.IntegerField(null=True, blank=True)
    subTitle = models.CharField(max_length=50)
    recommends = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='recommended_by',
        blank=True
    )

class Article(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    content = models.TextField(max_length=500)

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    content = models.CharField(max_length=100)