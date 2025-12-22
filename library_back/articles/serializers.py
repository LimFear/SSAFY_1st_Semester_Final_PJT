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
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Comment        
        fields = '__all__'
        read_only_fields = ('book', 'user',)

class FavoriteBookSerializer(serializers.ModelSerializer):      # TOP 5 전용
    book_title = serializers.CharField(source='book.title', read_only=True)
    count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Favorite
        fields = ('book_title', 'count')


class PopularBookSerializer(serializers.ModelSerializer):
    comment_count = serializers.IntegerField(read_only=True)
    score = serializers.IntegerField(read_only=True)

    class Meta:
        model = Book
        fields = ('comment_count', 'score', 'cover', 'views')
