from django.urls import path
from . import views

urlpatterns = [
    path('books/', views.books),
    path('books/<int:book_pk>/', views.books_detail),
    path('books/<int:book_pk>/comments/', views.comments),
    path('comments/<int:comment_pk>/', views.delete_comment),
    path('favorites/', views.favorite),
]
