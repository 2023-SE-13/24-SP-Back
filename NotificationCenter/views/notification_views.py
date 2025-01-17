from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from NotificationCenter.models import Notification


@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_notification(request):
    notification_id = request.GET.get('notification_id')
    notification = Notification.objects.get(notification_id=notification_id)
    if notification.notification_type == 'group_chat':
        group_id = notification.message.group.group_id
        message_id = notification.message.message_id
        notification_data = {
            "notification_id": notification.notification_id,
            "notification_type": "group_chat",
            "message_id": message_id,
            "group_id": group_id,
            "created_at": notification.created_at,
            "content": notification.content,
        }
    elif notification.notification_type == 'subscribe':
        tweet = notification.tweet
        position = notification.position
        tweet_id = tweet.tweet_id
        position_id = position.position_id
        notification_data = {
            "notification_id": notification.notification_id,
            "notification_type": "subscribe",
            "tweet_id": tweet_id,
            "position_id": position_id,
            "created_at": notification.created_at,
            "content": notification.content,
        }
    else:
        notification_data = {
            "notification_id": notification.notification_id,
            "notification_type": "system",
            "created_at": notification.created_at,
            "content": notification.content,
        }
    return Response({"status": "success", "data": notification_data}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_user_notifications(request):
    user = request.user
    require_type = request.GET.get('require_type')
    notifications = None
    if require_type == 'ALL':
        notifications = Notification.objects.filter(user=user)

    elif require_type == 'subscribe':
        notifications = Notification.objects.filter(user=user, notification_type='subscribe')

    elif require_type == 'system':
        notifications = Notification.objects.filter(user=user, notification_type='system')

    data = []
    for notification in notifications:
        data.append({
            "notification_id": notification.notification_id,
            "notification_type": notification.notification_type,
            "is_read": notification.is_read,
            "created_at": notification.created_at.strftime('%Y-%m-%d'),
            "content": notification.content,
            "company_name": get_attribute(notification.company, 'company_name', ''),
            "company_id": get_attribute(notification.company, 'company_id', ''),
            "position_name": get_attribute(notification.position, 'position_name', ''),
            "username": notification.user.username,
            'realname': notification.user.real_name,
            "position_id": get_attribute(notification.position, 'position_id', ''),
            "offer_id": get_attribute(notification.offer, 'offer_id', ''),
            "tweet_id": get_attribute(notification.tweet, 'tweet_id', ''),
            "message_id": get_attribute(notification.message, 'message_id', ''),
        })
    return Response({"status": "success", "data": data}, status=status.HTTP_200_OK)


def get_attribute(obj, attr_name, default=""):
    """获取模型属性，如果模型是None则返回默认值"""
    if obj is not None:
        return getattr(obj, attr_name, default)
    return default


@csrf_exempt
@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_notification(request):
    notification_id = request.GET.get('notification_id')
    is_read = request.GET.get('is_read')
    notification = Notification.objects.get(notification_id=notification_id)
    notification.is_read = is_read
    notification.save()
    return Response({"status": "success"}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_notification(request):
    notification_id = request.GET.get('notification_id')
    notification = Notification.objects.get(notification_id=notification_id)
    notification.delete()
    return Response({"status": "success"}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_read_notifications(request):
    user = request.user
    Notification.objects.filter(user=user, is_read=True).delete()
    return Response({"status": "success"}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def read_all_notifications(request):
    user = request.user
    Notification.objects.filter(user=user).update(is_read=True)
    return Response({"status": "success"}, status=status.HTTP_200_OK)