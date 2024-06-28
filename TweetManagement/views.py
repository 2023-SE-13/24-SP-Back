import json
import uuid

from django.core.files.base import ContentFile
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated

from TweetManagement.models import Tweet, TweetPhoto, Likes, Comment
from TweetManagement.serializers import TweetSerializer
from UserManagement.models import User
from shared.decorators import require_user, require_company, require_tweet, require_comment, require_textcontent


class TweetCURDViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Tweet.objects.all()
    serializer_class = TweetSerializer

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def create_tweet(request):
    user = request.user
    # formdata
    text_content = request.POST.get('text_content', None)
    tweet = Tweet.objects.create(user=user, text_content=text_content)
    try:
        # 从请求中获取图片文件列表
        photos = request.FILES.getlist('photos', None)
        if not photos:
            return JsonResponse({"status": "error", "message": "No photo file provided"},
                                status=status.HTTP_400_BAD_REQUEST)
        i = 0
        for photo in photos:
            # 创建新的推文图片文件名
            photo_type = photo.name.split('.')[-1]
            new_filename = f"{tweet.tweet_id}_tweetphoto_{i}.{photo_type}"
            i = i + 1
            # 读取和保存新文件
            new_file = ContentFile(photo.read())
            new_file.name = new_filename
            tweet_photo = TweetPhoto.objects.create(tweet=tweet)
            # 保存
            tweet_photo.photo.save(new_filename, new_file, save=True)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"An error occurred: {str(e)}"},
                            status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse({"status": "success", "message": "Tweet created successfully"}, status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
@require_tweet
def switch_tweetlike(request):
    user = request.user
    tweet = request.tweet_object
    like = Likes.objects.filter(tweet=tweet, user=user).first()
    if like:
        like.delete()
        tweet.likes -= 1
        tweet.save()
    else:
        Likes.objects.create(tweet=tweet, user=user)
        tweet.likes += 1
        tweet.save()
    return JsonResponse({"status": "success", "message": "Tweet like status switched successfully"}, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
@require_tweet
def delete_tweet(request):
    tweet = request.tweet_object
    tweet.delete()
    return JsonResponse({"status": "success", "message": "Tweet deleted successfully"}, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def retweet(request):
    user = request.user
    data = json.loads(request.body.decode('utf-8'))
    text_content = data.get('text_content', None)
    tweet_id = data.get('tweet_id', None)
    tweet = Tweet.objects.filter(tweet_id=tweet_id).first()
    Tweet.objects.create(user=user, text_content=text_content, is_retweet=True, retweet_id=tweet)
    tweet.retweets += 1
    tweet.save()
    return JsonResponse({"status": "success", "message": "Tweet retweeted successfully"}, status=status.HTTP_201_CREATED)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
@require_tweet
def comment_tweet(request):
    user = request.user
    tweet = request.tweet_object
    data = json.loads(request.body.decode('utf-8'))
    content = data.get('content', None)
    Comment.objects.create(tweet=tweet, sender=user, content=content)
    tweet.comments += 1
    tweet.save()
    return JsonResponse({"status": "success", "message": "Tweet commented successfully"}, status=status.HTTP_201_CREATED)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
@require_tweet
@require_comment
@require_textcontent
def comment_comment(request):
    user = request.user
    tweet = request.tweet_object
    comment = request.comment_object
    content = request.text_content

    Comment.objects.create(target_comment=comment, sender=user, content=content, tweet=tweet)
    tweet.comments += 1
    tweet.save()
    return JsonResponse({"status": "success", "message": "User commented successfully"}, status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
@require_tweet
@require_user
@require_comment
def comment_user(request):
    user = request.user
    tweet = request.tweet_object
    target_comment = request.comment_object
    target_user = request.user_object
    data = json.loads(request.body.decode('utf-8'))
    content = data.get('content', None)
    content = "回复 @" + target_user.username + " ：" + content
    Comment.objects.create(target_user=target_user, target_comment=target_comment, sender=user, content=content, tweet=tweet)
    tweet.comments += 1
    tweet.save()
    return JsonResponse({"status": "success", "message": "User commented successfully"}, status=status.HTTP_201_CREATED)
