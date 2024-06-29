from django.urls import path
from RecommendManagement.views import *

urlpatterns = [
    path('recommend_subscribe', recommend_subscribe),
]
