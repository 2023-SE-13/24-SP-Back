from django.urls import path
from RecommendManagement.views import *

urlpatterns = [
    path('recommend_subscribe', recommend_subscribe),
    path('recommend_position', recommend_position),
    path('recommend_simposition', recommend_simposition),
]
