from django.urls import path, include
from .views import CookieTokenObtainPairView, CookieTokenRefreshView
from . import views

urlpatterns = [
    path('signup/', include('dj_rest_auth.registration.urls')),
    path('signout/', views.signout),
    path('token/', CookieTokenObtainPairView.as_view()),
    path('token/refresh/', CookieTokenRefreshView.as_view()),
    path('logout/', views.logout),
]