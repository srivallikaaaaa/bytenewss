from django.urls import path,include
from .views import ArticleListView, ArticleDetailView
from . import views
app_name = 'news'


urlpatterns = [
    path('', ArticleListView.as_view(), name='home'),  # ✅ This name='home' must exist!
    path('<int:pk>/', ArticleDetailView.as_view(), name='article_detail'),
    path('history/', views.reading_history, name='reading_history'),
    # news/urls.py
    path('articles/<int:pk>/', ArticleDetailView.as_view(), name='article_detail'),
    path('summary-test/', views.summarize_example, name='summary-test'),
    path('article/<int:pk>/generate_summary/', views.generate_summary_view, name='generate_summary'),
    path('article/<int:pk>/feedback/', views.submit_summary_feedback, name='submit_summary_feedback'),
    



]