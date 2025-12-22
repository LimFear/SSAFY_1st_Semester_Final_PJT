from django.db import models
from django.conf import settings

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
    
    views = models.PositiveIntegerField(default=0)          # TOP5 추리기 위한 조회수 검색 변수

# class Article(models.Model):  
#     book = models.ForeignKey(Book, on_delete=models.CASCADE)
#     title = models.CharField(max_length=50)
#     content = models.TextField(max_length=500)
#     created_at = models.DateField(auto_now_add=True)
#     updated_at = models.DateField(auto_now=True)

class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    content = models.CharField(max_length=100)
    created_at = models.DateField(auto_now_add=True)

class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'book',)
    
    def __str__(self):
        return f'{self.user.username} - {self.book.title}'
    
    def increment(self):
        self.count += 1
        self.save()

    def decrement(self):
        self.count += 1
        self.save()