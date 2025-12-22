from django.shortcuts import render
from django.db import connection, transaction

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from articles.models import Comment

# Create your views here.

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def signout(request):
    print("===========")
    print(f'delete : {request.user}')
    print("===========")
    user = request.user
    try:
        Comment.objects.filter(user=user).delete()

        with connection.cursor() as cursor:
            cursor.execute("PRAGMA foreign_keys = OFF;")
            try:
                user.delete()
            finally:
                cursor.execute("PRAGMA foreign_keys = ON;")

        print("...Complete!")
        
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response
    
    except Exception as e:
        print(type(e))
        print(e)
        return Response(
            {'error': 'Error!', 'details': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    response = Response(
        {'message': 'Logout completed'},
        status=status.HTTP_200_OK
    )
    response.delete_cookie('refresh_token')
    response.delete_cookie('access_token')
    return response

class CookieTokenObtainPairView(TokenObtainPairView):

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data['user_id'] = user.pk
        data['username'] = user.username
        return data

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        access = response.data.get('access')
        response.set_cookie(
            key='access_token',
            value=access,
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=60 * 5,
            path='/',
            domain='127.0.0.1'
        )

        refresh = response.data.get('refresh')
        response.set_cookie(
            key='refresh_token',
            value=refresh,
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=7 * 24 * 60 * 60,
            path='/',
            domain='127.0.0.1'
        )

        response.data = {
            "access": access,
        }

        print(response.data)

        return response
    
class CookieTokenRefreshView(TokenRefreshView):

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data['user_id'] = user.pk
        data['username'] = user.username
        return data

    def post(self, request, *args, **kwargs):
        refresh = request.COOKIES.get('refresh_token')

        if not refresh:
            return Response({"detail": "No refresh token"}, status=401)

        request.data['refresh'] = refresh
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access = response.data.get('access')
            response.set_cookie(
                key='access_token',
                value=access,
                httponly=True,
                secure=False,
                samesite='Lax',
                max_age=60 * 5,
            )
        return response
