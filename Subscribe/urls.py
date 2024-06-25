from django.urls import path
from . import views

urlpatterns = [
    path('subscribe_company/', views.Subscribe_company, name='subscribe_company'),
    path('subscribe_user/', views.Subscribe_user, name='subscribe_user'),
]