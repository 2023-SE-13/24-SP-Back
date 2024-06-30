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
from rest_framework import status

from NotificationCenter.views.utils.notifications import create_notification
from Subscribe.models import SubscribeUser, SubscribeCompany
from TweetManagement.models import Tweet, TweetPhoto, Likes, Comment
from TweetManagement.serializers import TweetSerializer
from UserManagement.models import User
from CompanyManagement.models import CompanyMember
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
        if photos:
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
    # 向关注该用户的所有用户推送通知
    user_subscribers = SubscribeUser.objects.filter(user_dst=user)
    for subscriber in user_subscribers:
        create_notification(json.dumps({
            "username": subscriber.user_src.username,
            "notification_type": "subscribe",
            "content": f"User {user.username} has created a new tweet",
            "tweet_id": str(tweet.tweet_id)
        }))

    # 向关注该用户所属公司的所有用户推送通知
    company_member = CompanyMember.objects.filter(user=user).first()
    if company_member:
        company_subscriber = SubscribeCompany.objects.filter(company=company_member.company)
        for subscriber in company_subscriber:
            create_notification(json.dumps({
                "username": subscriber.user.username,
                "notification_type": "subscribe",
                "content": f"Company {subscriber.company.company_name} has created a new tweet",
                "tweet_id": str(tweet.tweet_id)
            }))

    return JsonResponse({"status": "success", "message": "Tweet created successfully", "tweet_id": tweet.tweet_id},
                        status=status.HTTP_201_CREATED)


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
    return JsonResponse({"status": "success", "message": "Tweet like status switched successfully"},
                        status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
@require_tweet
def delete_tweet(request):
    tweet = request.tweet_object
    user = request.user
    if tweet.user != user:
        return JsonResponse({"status": "error", "message": "You are not allowed to delete this tweet"},
                            status=status.HTTP_400_BAD_REQUEST)
    tweet.delete()
    return JsonResponse({"status": "success", "message": "Tweet deleted successfully"}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
@require_tweet
@require_textcontent
def comment_tweet(request):
    user = request.user
    tweet = request.tweet_object
    content = request.text_content
    Comment.objects.create(tweet=tweet, sender=user, content=content)
    tweet.comments += 1
    tweet.save()
    return JsonResponse({"status": "success", "message": "Tweet commented successfully"},
                        status=status.HTTP_201_CREATED)


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
@require_textcontent
def comment_user(request):
    user = request.user
    tweet = request.tweet_object
    target_comment = request.comment_object
    target_user = request.user_object
    content = request.text_content
    content = "回复 @" + target_user.username + " ：" + content
    Comment.objects.create(target_user=target_user, target_comment=target_comment, sender=user, content=content,
                           tweet=tweet)
    tweet.comments += 1
    tweet.save()
    return JsonResponse({"status": "success", "message": "User commented successfully"}, status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['GET'])
@require_company
def get_company_tweet(request):
    company = request.company_object
    members = CompanyMember.objects.filter(company=company).values_list('user_id', flat=True)
    company_tweets = Tweet.objects.filter(user_id__in=members).order_by('-created_at')
    data = []
    for company_tweet in company_tweets:
        data.append(
            company_tweet.tweet_id
        )
    return JsonResponse({"status": "success", "data": data}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
@require_tweet
def get_tweet_comment(request):
    tweet = request.tweet_object
    comments = Comment.objects.filter(tweet=tweet)
    data = []
    for comment in comments:
        children_comment_id = list(Comment.objects.filter(target_comment=comment).values_list('comment_id', flat=True))
        data.append(
            {
                "comment_id": comment.comment_id,
                "comment_sender": comment.sender.username,
                "content": comment.content,
                "createTime": comment.created_at,
                "children_list": children_comment_id,
            }
        )
    return JsonResponse({"status": "success", "data": data}, status=status.HTTP_200_OK)


# TODO

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
@require_tweet
def get_tweet(request):
    tweet = request.tweet_object
    data = TweetSerializer(tweet).data
    if Likes.objects.filter(tweet=tweet, user=request.user).exists():
        data["is_like"] = True
    else:
        data["is_like"] = False
    return JsonResponse({"status": "success", "data": data},  status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
@require_comment
def get_comment(request):
    comment = request.comment_object
    data = {
        "comment_id": comment.comment_id,
        "sender": comment.sender.username,
        "content": comment.content,
        "createTime": comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        "children_comment": [],
    }
    children_comment = Comment.objects.filter(target_comment=comment).order_by('-created_at')
    for child in children_comment:
        child_data = {
            "comment_id": child.comment_id,
            "sender": child.sender.username,
            "content": child.content,
            "createTime": child.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
        data["children_comment"].append(child_data)

    return JsonResponse({"status": "success", "data": data}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
@require_user
def get_user_tweet(request):
    user = request.user_object
    user_tweets = Tweet.objects.filter(user=user).order_by('-created_at')
    data = []
    for user_tweet in user_tweets:
        data.append(
            user_tweet.tweet_id
        )
    return JsonResponse({"status": "success", "data": data}, status=status.HTTP_200_OK)
