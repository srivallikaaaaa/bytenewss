from django.urls import path,include
from .views import ArticleListView, ArticleDetailView
from . import views


app_name = 'news'


urlpatterns = [
    path('', ArticleListView.as_view(), name='home'),
    path('<int:pk>/', ArticleDetailView.as_view(), name='article_detail'),
    path('history/', views.reading_history, name='reading_history'),
    path('articles/<int:pk>/', ArticleDetailView.as_view(), name='article_detail'),
    path('generate-summary/<int:pk>/', views.generate_summary_view, name='generate_summary'),  # ✅ Added
    path('article/<int:pk>/generate_summary/', views.generate_summary_view, name='generate_summary'),
    path('article/<int:pk>/feedback/', views.submit_summary_feedback, name='submit_summary_feedback'),
    path('article/<int:pk>/generate_audio_ajax/', views.generate_audio_ajax, name='generate_audio_ajax'),

   
    path('', views.landing_page, name='home'),


]