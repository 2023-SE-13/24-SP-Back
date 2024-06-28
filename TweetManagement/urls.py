
from django.urls import path, include
from rest_framework.routers import DefaultRouter


# 创建一个 router 并注册 ViewSet
from TweetManagement.views import *

router = DefaultRouter()
router.register(r'tweets', TweetCURDViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('create_tweet', create_tweet),
    path('switch_tweetlike', switch_tweetlike),
    path('delete_tweet', delete_tweet),
    path('retweet', retweet),
    path('comment_tweet', comment_tweet),
    path('comment_user', comment_user),
    path('comment_comment', comment_comment),
]
