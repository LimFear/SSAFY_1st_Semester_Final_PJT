from rest_framework import serializers
from .models import Book, Category, Comment, Favorite

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('title', 'author', 'cover', 'id')

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

class FavoriteBookSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Favorite
        fields = ('book_title', 'count')