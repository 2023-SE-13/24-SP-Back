from django.urls import path
from RecommendManagement.views import *

urlpatterns = [
    path('recommend_company_user', recommend_company_user),
]
