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

class FavoriteBookSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Favorite
        fields = ('book_title', 'count')

class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

        from rest_framework import serializers
from .models import Book

class PopularBookSerializer(serializers.ModelSerializer):           # TOP 5 구현
    comment_count = serializers.IntegerField(read_only=True)
    score = serializers.IntegerField(read_only=True)

    class Meta:
        model = Book
        # ✅ 프론트에서 상세 이동하려면 id가 반드시 필요
        fields = ("id", "title", "author", "cover", "views", "comment_count", "score")
