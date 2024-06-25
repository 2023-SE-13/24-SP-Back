from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
import json
from shared.decorators import require_user, require_company
from .serializers import SubscribeCompanySerializer
from .serializers import SubscribeUserSerializer
from .models import Subscribe_user
from .models import Subscribe_company
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import viewsets, status


class Subscribe_userCURDViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Subscribe_user.objects.all()
    serializer_class = SubscribeUserSerializer

class Subscribe_companyCURDViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Subscribe_company.objects.all()
    serializer_class = SubscribeCompanySerializer


@api_view(['POST'])
@csrf_exempt
@require_user
@require_company
def subscribe_company(request):
    if request.method == 'POST':
        company = request.company_object
        user = request.user_object
        subscribe = Subscribe_company(company = company,user=user)
        subscribe.save()
        return Response({'status':'success'}, status=status.HTTP_201_CREATED)
    return Response({'status': 'Method Not Allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
@csrf_exempt
@require_user
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def subscribe_user(request):
    if request.method == 'POST':
        user_1 = request.user
        user_2 = request.user_object
        subscribe = Subscribe_user(user_src=user_1,user_dst=user_2)
        subscribe.save()
        return Response({'status': 'success'}, status=status.HTTP_201_CREATED)
    return Response({'status': 'Method Not Allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)