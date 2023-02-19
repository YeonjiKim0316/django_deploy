"""django_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('blog.urls')),
    path("admin/", admin.site.urls),
    path('blog/', include('blog.urls')), # blog 폴더 안의 urls(.py)를 참조해줘 라는 뜻
    path('markdownx/', include('markdownx.urls')),# markdown 위해 추가 -> blog/models.py도 변경
    
    path('accounts/', include('allauth.urls')),
    # path('firetest/', include('firebase_auth.urls'), name='fire_base_test'),

]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)