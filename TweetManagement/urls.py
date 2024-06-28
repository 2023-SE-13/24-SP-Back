
from django.urls import path, include
from rest_framework.routers import DefaultRouter


# 创建一个 router 并注册 ViewSet
from TweetManagement.views import *

router = DefaultRouter()
router.register(r'tweets', TweetCURDViewSet)

urlpatterns = [
    path('', include(router.urls)),    
]
