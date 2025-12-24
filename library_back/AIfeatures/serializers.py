from rest_framework import serializers

class RecommendationSerializer(serializers.Serializer):

    answer = serializers.CharField()