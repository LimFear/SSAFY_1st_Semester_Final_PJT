from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.contrib.auth import get_user_model
from .models import Book, Comment

from .serializers import BookSerializer, BookDetailSerializer
from .serializers import CommentSerializer

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
        comment_list = get_list_or_404(Comment, book_id=book_pk)
        serializer = CommentSerializer(comment_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif (request.method == 'POST'):

        if (request.user.is_authenticated):
            user = request.user
        else :
            User = get_user_model()
            user, created = User.objects.get_or_create(username='guest')
        serializer = CommentSerializer(data=request.data)
        if (serializer.is_valid(raise_exception=True)):
            serializer.save(book_id=book_pk, user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
def delete_comment(request, comment_pk):
    if (request.method == 'DELETE'):
        comment = get_object_or_404(Comment, pk=comment_pk)
        # if (comment.user == request.user):
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)