from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from UserManagement.models import Message, User
from UserManagement.serializers import MessageSerializer


@csrf_exempt
@api_view(['POST'])
def save_message(request):
    data = request.data
    sender_uname = data.get('sender_uname')
    receiver_uname = data.get('receiver_uname')
    content = data.get('content')
    timestamp = timezone.now()
    now_str = timezone.now().strftime('%Y%m%d%H%M%S')
    if not all([sender_uname, receiver_uname, content]):
        return JsonResponse({'status': 'error', 'message': 'Missing parameter'}, status=400)
    message = Message.objects.create(sender=User.objects.get(username=sender_uname),
                                        receiver=User.objects.get(username=receiver_uname),
                                        content=content, timestamp=timestamp)
    return JsonResponse({'status': 'success', 'message_id': message.message_id, 'timestamp': now_str},
                        status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_messages(request):
    receiver_uname = request.user.username
    sender_uname = request.user.username
    messages = Message.objects.filter(
        Q(sender__username=sender_uname, receiver__username=receiver_uname) |
        Q(sender__username=receiver_uname, receiver__username=sender_uname)
    ).order_by('-timestamp')

    serializer = MessageSerializer(messages, many=True)

    return JsonResponse(serializer.data, safe=False)
