from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from UserManagement.models import Message, User, Conversation
from UserManagement.serializers import MessageSerializer, ConversationSerializer
from shared.decorators import require_user
import pytz


@csrf_exempt
@api_view(['POST'])
def save_message(request):
    data = request.data
    sender_uname = data.get('sender_uname')
    receiver_uname = data.get('receiver_uname')
    conversation_id = data.get('conversation_id')
    content = data.get('content')
    tz = pytz.timezone('Asia/Shanghai')
    timestamp = timezone.now().astimezone(tz)
    if not all([sender_uname, receiver_uname, content, conversation_id]):
        return JsonResponse({'status': 'error', 'message': 'Missing parameter'}, status=400)
    con = Conversation.objects.get(conversation_id=conversation_id)

    if not ({sender_uname, receiver_uname} == {con.user1.username, con.user2.username}):
        return JsonResponse({'status': 'error', 'message': 'Sender or receiver is not in the conversation'}, status=400)

    message = Message.objects.create(sender=User.objects.get(username=sender_uname),
                                        receiver=User.objects.get(username=receiver_uname),
                                        conversation=Conversation.objects.get(conversation_id=conversation_id),
                                        content=content, timestamp=timestamp)
    con.last_message_time = timestamp
    con.save()
    return JsonResponse({'status': 'success', 'message_id': message.message_id, 'timestamp': timestamp},
                        status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_conversations(request):
    cur_user = request.user
    conversations = Conversation.objects.filter(Q(user1=cur_user) | Q(user2=cur_user)).order_by('-last_message_time')
    serializer = ConversationSerializer(conversations, many=True)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_user
def create_conversation(request):
    sender = request.user
    receiver = request.user_object
    if sender.username == receiver.username:
        return JsonResponse({"status": "error", "message": "You cannot create a private chat with yourself", "conversation_id": ""},
                            status=status.HTTP_400_BAD_REQUEST)
    if Conversation.objects.filter(user1__in={sender, receiver}, user2__in={sender, receiver}).exists():
        return JsonResponse({"status": "success",
                             "message": "Private chat already exists",
                             "conversation_id": Conversation.objects.get(Q(user1=sender, user2=receiver) | Q(user1=receiver, user2=sender)).conversation_id},
                            status=status.HTTP_200_OK)
    tz = pytz.timezone('Asia/Shanghai')
    utc8time = timezone.now().astimezone(tz)
    conversation = Conversation.objects.create(user1=sender, user2=receiver, last_message_time=utc8time)
    return JsonResponse({"status": "success",
                         "message": "Private chat created successfully",
                         "conversation_id": conversation.conversation_id},
                        status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_messages(request):
    conversation_id = request.GET.get('conversation_id')
    if not conversation_id:
        return JsonResponse({'status': 'error', 'message': 'Missing conversation_id parameter'}, status=400)
    messages = Message.objects.filter(conversation_id=conversation_id).order_by('-timestamp')
    serializer = MessageSerializer(messages, many=True)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)

