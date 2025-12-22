from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from articles.models import Category

# class CustomRegisterSerializer(RegisterSerializer):
#     category = serializers.ModelMultipleChoiceField(
#         queryset=Category.objects.all(), 
#         required=True
#     )

#     def get_cleaned_data(self):
#         data = super().get_cleaned_data()
#         data['category'] = self.validated_data.get('category')
#         return data