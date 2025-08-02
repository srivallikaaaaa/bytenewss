"""
URL configuration for bytenews project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from users import views as user_views
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from news.views import landing_page
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from news.views import ArticleViewSet,UserPreferenceViewSet
from news.views import GenerateAudioAPIView 

router = routers.DefaultRouter()
router.register(r'articles', ArticleViewSet)
router.register(r'preferences', UserPreferenceViewSet, basename='userpreference')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('', include('news.urls')),

    path('api/', include(router.urls)),
    path('api/articles/<int:pk>/generate_audio/', GenerateAudioAPIView.as_view(), name='api_generate_audio'),



    path('news/', include('news.urls')),
    path('accounts/', include('allauth.urls')),
    path('api/', include(router.urls)),
  

    



    # ✅ Home page goes to landing page
    path('', landing_page, name='landing'),

    # ✅ Article list at /articles/
    path('articles/', include('news.urls')),

    # ✅ Auth routes
    path('register/', user_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logged_out.html'), name='logout'),
    path('logged_out/', TemplateView.as_view(template_name='registration/logged_out.html')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


