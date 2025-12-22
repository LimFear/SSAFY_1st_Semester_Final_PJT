from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from django.conf import settings
from articles.models import Category

class CustomUserSerializer(RegisterSerializer):
    categories = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=True)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data['categories'] = self.validated_data.get('categories')
        return data
    
    def save(self, request):
        user = super().save(request)
        categories_data = self.validated_data.get('categories')
        if categories_data:
            user.categories.set(categories_data)
        return user

    class Meta:
        model = settings.AUTH_USER_MODEL
        fields = ['id', 'username', 'email', 'categories']