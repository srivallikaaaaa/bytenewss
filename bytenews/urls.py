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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('news/', include('news.urls')),
    path('articles/', include(('news.urls', 'news'), namespace='news')),

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