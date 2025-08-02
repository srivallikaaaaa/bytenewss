# news/serializers.py
from rest_framework import serializers
from .models import Article, Category, SummaryFeedback
from .models import UserPreference, Category

class ArticleSerializer(serializers.ModelSerializer):
    categories = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'title', 'summary', 'link', 'publication_date', 'author', 'source', 'categories', 'audio_file']


class UserPreferenceSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=True)

    class Meta:
        model = UserPreference
        fields = ['id', 'user', 'categories']
        read_only_fields = ['user']  