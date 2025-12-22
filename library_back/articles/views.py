from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from django.contrib.auth import get_user_model
from .models import Book, Comment, Favorite

from .serializers import BookSerializer, BookDetailSerializer
from .serializers import CommentSerializer, FavoriteBookSerializer

# Create your views here.

@api_view(['GET'])
def books(request):
    if (request.method == 'GET'):
        book_list = get_list_or_404(Book)
        serializer = BookSerializer(book_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def books_detail(request, book_pk):
    if (request.method == 'GET'):
        book = get_object_or_404(Book, pk=book_pk)
        serializer = BookDetailSerializer(book)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
def comments(request, book_pk):
    if (request.method == 'GET'):
        # comment_list = get_list_or_404(Comment, book_id=book_pk)
        # 댓글이 없어도 404 말고 빈 리스트 반환
        comment_list = Comment.objects.filter(book_id=book_pk).order_by('-id')
        serializer = CommentSerializer(comment_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # POST
    if not request.user.is_authenticated:
        return Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

    serializer = CommentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(book_id=book_pk, user=request.user)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
def delete_comment(request, comment_pk):
    if not request.user.is_authenticated:
        return Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

    comment = get_object_or_404(Comment, pk=comment_pk)

    if comment.user_id != request.user.id:
        return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

    comment.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
