from rest_framework import serializers
from .models import Book, Category, Comment

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('title', 'author')

class BookDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    class Meta:
        model = Book
        fields = '__all__'
        read_only_fields = ('category',)

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('book', 'user',)