from django.shortcuts import render, get_list_or_404, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

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

@api_view(['GET', 'POST', 'DELETE'])
def comments(request, book_pk):
    if (request.method == 'GET'):
        article_list = get_list_or_404(Comment, pk=book_pk)
        serializer = CommentSerializer(article_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif (request.method == 'POST'):
        serializer = CommentSerializer(data=request.data)
        if (serializer.is_valid(raise_exception=True)):
            serializer.save(book_id=book_pk)
            return Response(serializer.data, status=status.HTTP_201_CREATED)