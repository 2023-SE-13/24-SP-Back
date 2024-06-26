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
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_company
def subscribe_company(request):
    if request.method == 'POST':
        company = request.company_object
        user = request.user
        if not Subscribe_company.objects.filter(company=company, user=user).exists():
            subscribe = Subscribe_company(company=company,user=user)
            company.company_subscription = company.company_subscription + 1
            company.save()
            subscribe.save()
        else:
            return Response({"status": "fail", "message": "The company is subscribed"})
        return Response({'status':'success'}, status=status.HTTP_201_CREATED)
    return Response({'status': 'Method Not Allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['DELETE'])
@csrf_exempt
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_company
def unsubscribe_company(request):
    if request.method == 'DELETE':
        company = request.company_object
        user = request.user
        if Subscribe_company.objects.filter(company=company, user=user).exists():
            subscribe = Subscribe_company.objects.get(company=company,user=user)
            company.company_subscription = company.company_subscription - 1
            company.save()
            subscribe.delete()
        else:
            return Response({"status": "fail", "message": "The company is not subscribed"})
        return Response({'status': 'success'}, status=status.HTTP_201_CREATED)
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
        if not Subscribe_user.objects.filter(user_src=user_1, user_dst=user_2).exists():
            subscribe = Subscribe_user(user_src=user_1,user_dst=user_2)
            user_2.user_subscription = user_2.user_subscription + 1
            user_2.save()
            subscribe.save()
        else:
            return Response({"status": "fail", "message": "The user is subscribed"})
        return Response({'status': 'success'}, status=status.HTTP_201_CREATED)
    return Response({'status': 'Method Not Allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['DELETE'])
@csrf_exempt
@require_user
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def unsubscribe_user(request):
    if request.method == 'DELETE':
        user_1 = request.user
        user_2 = request.user_object
        if Subscribe_user.objects.filter(user_src=user_1, user_dst=user_2).exists():
            subscribe = Subscribe_user.objects.get(user_src=user_1, user_dst=user_2)
            user_2.user_subscription = user_2.user_subscription - 1
            user_2.save()
            subscribe.delete()
        else:
            return Response({"status": "fail", "message": "The user is not subscribed"})
        return Response({'status': 'success'}, status=status.HTTP_201_CREATED)
    return Response({'status': 'Method Not Allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)