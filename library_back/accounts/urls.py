from django.urls import path, include
from .views import CookieTokenObtainPairView, CookieTokenRefreshView
from . import views

urlpatterns = [
    # Token Auth urls
    # path('', include('dj_rest_auth.urls')),

    path('signup/', include('dj_rest_auth.registration.urls')),
    path('signout/', views.signout),
    # Simple JWT urls
    path('token/', CookieTokenObtainPairView.as_view()),
    path('token/refresh/', CookieTokenRefreshView.as_view()),
]