from django.shortcuts import get_list_or_404, get_object_or_404
from django.db.models import Count, F
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Book, Category, Comment, Favorite
from .serializers import (
    BookSerializer,
    BookDetailSerializer,
    CommentSerializer,
    FavoriteBookSerializer,
    CategoryListSerializer,
    PopularBookSerializer,
)


def _popular_queryset():
    # 기존 인기 TOP5 로직을 함수로 분리
    return (
        Book.objects
        .annotate(comment_count=Count("comment"))  # 기존 코드 유지(현재 프로젝트에 맞춘 상태라고 가정)
        .annotate(score=F("views") + F("comment_count"))
        .order_by("-score", "-views", "-comment_count", "-id")
    )


@api_view(["GET"])
def popular_books(request):
    book_queryset = _popular_queryset()[:5]
    serializer = PopularBookSerializer(book_queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def recommended_books(request):
    """
    로그인 후:
    - 즐겨찾기 작가(author) 기준으로 다른 도서 추천
    - 즐겨찾기 없으면 인기 TOP5로 fallback
    """
    user = request.user

    favorite_book_ids = list(
        Favorite.objects.filter(user=user).values_list("book_id", flat=True)
    )

    # 즐겨찾기 없으면 인기 TOP5 그대로 반환
    if not favorite_book_ids:
        serializer = BookSerializer(_popular_queryset()[:5], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    favorite_authors = list(
        Book.objects.filter(id__in=favorite_book_ids)
        .values_list("author", flat=True)
        .distinct()
    )

    # 추천: 같은 작가의 다른 책(즐겨찾기 제외)
    rec_qs = (
        Book.objects.filter(author__in=favorite_authors)
        .exclude(id__in=favorite_book_ids)
        .order_by("-views", "-id")
    )

    recommended_list = list(rec_qs[:5])

    # 5개 미만이면 인기에서 채우기(중복/즐겨찾기 제외)
    if len(recommended_list) < 5:
        used_ids = set(favorite_book_ids) | {b.id for b in recommended_list}
        filler_qs = _popular_queryset().exclude(id__in=used_ids)
        recommended_list.extend(list(filler_qs[: 5 - len(recommended_list)]))

    serializer = BookSerializer(recommended_list, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def books(request):
    book_list = get_list_or_404(Book)
    serializer = BookSerializer(book_list, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def books_detail(request, book_pk):
    Book.objects.filter(pk=book_pk).update(views=F("views") + 1)
    book = get_object_or_404(Book, pk=book_pk)
    serializer = BookDetailSerializer(book)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET", "POST"])
def comments(request, book_pk):
    if request.method == "GET":
        comment_list = Comment.objects.filter(book_id=book_pk).order_by("-id")
        serializer = CommentSerializer(comment_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # POST
    if not request.user.is_authenticated:
        return Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

    serializer = CommentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(book_id=book_pk, user=request.user)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["DELETE"])
def delete_comment(request, comment_pk):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    comment = get_object_or_404(Comment, pk=comment_pk)
    if comment.user_id != request.user.id:
        return Response(status=status.HTTP_403_FORBIDDEN)

    comment.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST"])
def favorite(request):
    user = request.user

    if request.method == "GET":
        favorite_books = Favorite.objects.filter(user=user)
        books = [favorite.book for favorite in favorite_books]
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # POST
    book_pk = request.data.get("book_pk")
    book = get_object_or_404(Book, pk=book_pk)

    favorite_qs = Favorite.objects.filter(user=user, book=book)
    if favorite_qs.exists():
        favorite_qs.delete()
        return Response({"detail": "Book removed from favorites."}, status=status.HTTP_204_NO_CONTENT)

    Favorite.objects.create(user=user, book=book)
    return Response({"detail": "Book added to favorites."}, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def categories(request):
    category_list = get_list_or_404(Category)
    serializer = CategoryListSerializer(category_list, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
