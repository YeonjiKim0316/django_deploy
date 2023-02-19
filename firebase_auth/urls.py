from django.urls import path, include
from . import views
app_name = "firebase_auth"

urlpatterns = [
    path('', views.firebase_test, name="test"),
]