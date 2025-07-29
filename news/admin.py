from django.contrib import admin

# Register your models here.
#news/admin.py:

from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Category, Article, UserPreference, ReadingHistory
from .models import SummaryFeedback


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'published_date', 'created_at']
    list_filter = ['category', 'published_date']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at']

@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user']
    filter_horizontal = ['preferred_categories']

@admin.register(ReadingHistory)
class ReadingHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'article', 'read_at']
    list_filter = ['read_at']
    readonly_fields = ['read_at']


@admin.register(SummaryFeedback)
class SummaryFeedbackAdmin(admin.ModelAdmin):
    list_display = ['user', 'article', 'is_helpful', 'feedback_date']
    list_filter = ['is_helpful', 'feedback_date']
    search_fields = ['user__username', 'article__title']