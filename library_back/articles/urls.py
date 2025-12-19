from django.urls import path
from . import views

urlpatterns = [
    path('books/', views.books),
    path('books/<int:book_pk>/', views.books_detail),
    path('comments/<int:book_pk>/', views.comments),
]
