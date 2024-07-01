import os

from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
import json

from CompanyManagement.models import CompanyMember
from shared.decorators import require_user, require_company
from .serializers import SubscribeCompanySerializer
from .serializers import SubscribeUserSerializer
from .models import SubscribeUser
from .models import SubscribeCompany
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import viewsets, status


class SubscribeUserCURDViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = SubscribeUser.objects.all()
    serializer_class = SubscribeUserSerializer

class SubscribeCompanyCURDViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = SubscribeCompany.objects.all()
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
        if not SubscribeCompany.objects.filter(company=company, user=user).exists():
            subscribe = SubscribeCompany(company=company,user=user)
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
        if SubscribeCompany.objects.filter(company=company, user=user).exists():
            subscribe = SubscribeCompany.objects.get(company=company,user=user)
            company.company_subscription = company.company_subscription - 1
            company.save()
            subscribe.delete()
        else:
            return Response({"status": "fail", "message": "The company is not subscribed"})
        return Response({'status': 'success'}, status=status.HTTP_201_CREATED)
    return Response({'status': 'Method Not Allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
@csrf_exempt
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_company
def do_subscribed_company(request):
    if request.method == 'POST':
        user = request.user
        company = request.company_object
        if SubscribeCompany.objects.filter(company=company, user=user).exists():
            return Response({'status': 'success'}, status=status.HTTP_201_CREATED)
        else:
            return Response({"status": "fail"}, status=status.HTTP_201_CREATED)
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
        if not SubscribeUser.objects.filter(user_src=user_1, user_dst=user_2).exists():
            subscribe = SubscribeUser(user_src=user_1,user_dst=user_2)
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
        if SubscribeUser.objects.filter(user_src=user_1, user_dst=user_2).exists():
            subscribe = SubscribeUser.objects.get(user_src=user_1, user_dst=user_2)
            user_2.user_subscription = user_2.user_subscription - 1
            user_2.save()
            subscribe.delete()
        else:
            return Response({"status": "fail", "message": "The user is not subscribed"})
        return Response({'status': 'success'}, status=status.HTTP_201_CREATED)
    return Response({'status': 'Method Not Allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
@csrf_exempt
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_user
def do_subscribed_user(request):
    if request.method == 'POST':
        user_1 = request.user
        user_2 = request.user_object
        if SubscribeUser.objects.filter(user_src=user_1, user_dst=user_2).exists():
            return Response({'status': 'success'}, status=status.HTTP_201_CREATED)
        else:
            return Response({"status": "fail"}, status=status.HTTP_201_CREATED)
    return Response({'status': 'Method Not Allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
@csrf_exempt
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_subscribe_user(request):
    user = request.user
    subscribe_users = SubscribeUser.objects.filter(user_src=user)
    data = []
    for subscribe_user in subscribe_users:
        data.append({
            "username": subscribe_user.user_dst.username,
            "avatar": os.path.basename(subscribe_user.user_dst.avatar.name),
            "company_name": CompanyMember.objects.get(user=subscribe_user).company.company_name if CompanyMember.objects.filter(user=subscribe_user).exists() else "",
        })
    return Response({"status": "success", "data": data}, status=status.HTTP_200_OK)

@api_view(['GET'])
@csrf_exempt
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_subscribe_company(request):
    user = request.user
    subscribe_companies = SubscribeCompany.objects.filter(user=user)
    data = []
    for subscribe_company in subscribe_companies:
        data.append({
            "company_id": subscribe_company.company.company_id,
            "company_name": subscribe_company.company.company_name,
            "company_image": os.path.basename(subscribe_company.company.company_image.name),
            "company_description": subscribe_company.company.company_description,
        })
    return Response({"status": "success", "data": data}, status=status.HTTP_200_OK)

