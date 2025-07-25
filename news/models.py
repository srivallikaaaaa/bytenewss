from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    summary = models.TextField(blank=True)
    source_url = models.URLField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    published_date = models.DateTimeField(default=timezone.now)
    summary = models.TextField(blank=True, null=True)
    
    # ✅ Only this link field should exist
    link = models.URLField(max_length=500, unique=True, null=True, blank=True)

    publication_date = models.DateTimeField(null=True, blank=True)
    author = models.CharField(max_length=255, default='Unknown')
    source = models.CharField(max_length=100, default='Unknown')  # ✅ New field

    created_at = models.DateTimeField(auto_now_add=True)
    audio_file = models.FileField(upload_to='audio/', blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-published_date']


class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferred_categories = models.ManyToManyField(Category, blank=True)

    def __str__(self):
        return f"{self.user.username}'s preferences"


class ReadingHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} read {self.article.title}"

    class Meta:
        unique_together = ('user', 'article')


class SummaryFeedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    is_helpful = models.BooleanField()
    feedback_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'article')
        verbose_name_plural = "Summary Feedback"

    def __str__(self):
        return f"{self.user.username} - {self.article.title[:30]} - Helpful: {self.is_helpful}"
