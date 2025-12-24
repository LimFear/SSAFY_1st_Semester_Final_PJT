from rest_framework import serializers
from .models import Book, Category, Comment, Favorite


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ("id", "title", "author", "cover")


class BookDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Book
        fields = "__all__"
        read_only_fields = ("category",)


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ("book", "user")


class FavoriteBookSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source="book.title", read_only=True)
    count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Favorite
        fields = ("book_title", "count")


class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class PopularBookSerializer(serializers.ModelSerializer):
    comment_count = serializers.IntegerField(read_only=True)
    score = serializers.IntegerField(read_only=True)

    class Meta:
        model = Book
        # 프론트에서 바로 쓰게 id/title/author/cover 포함
        fields = ("id", "title", "author", "cover", "views", "comment_count", "score")
