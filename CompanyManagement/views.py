import json

from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated

from CompanyManagement.models import Company, CompanyMember
from CompanyManagement.serializer import CompanySerializer, CompanyMemberUserSerializer
from UserManagement.models import User
from CompanyManagement.models import JoinVerification
from shared.decorators import require_user, require_company


# Create your views here.

class CompanyCURDViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = User.objects.all()
    serializer_class = CompanySerializer


class CompanyMemberCURDViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = CompanyMember.objects.all()
    serializer_class = CompanyMemberUserSerializer


@api_view(['PUT'])
@csrf_exempt
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_company(request):
    data = json.loads(request.body.decode('utf-8'))
    company_name = data.get('company_name')
    company_description = data.get('company_description')
    if not company_name or not company_description:
        return JsonResponse(
            {"status": "error", "message": "company_name, company_description are required"},
            status=status.HTTP_400_BAD_REQUEST)

    company = Company.objects.filter(company_name=company_name)
    if company.exists():
        return JsonResponse({"status": "error", "message": "Company name already exists"},
                            status=status.HTTP_409_CONFLICT)

    company = Company(company_name=company_name, company_description=company_description)
    company.save()
    # company_id = company.company_id
    # 设置默认image
    # default_image_path = 'resources/company_images/default_image.png'
    # with open(default_image_path, 'rb') as f:
    #     image_content = f.read()
    # new_filename = f"{company_id}_image.png"
    # new_file = ContentFile(image_content)
    # new_file.name = new_filename
    # company.company_image.save(new_filename, new_file, save=True)

    # 将创建者加入Company
    user = request.user
    company_member = CompanyMember(company=company, user=user, role='Creator')
    company_member.save()
    user.is_staff = True
    user.save()

    return JsonResponse({'status': 'success'}, status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_company
@require_user
# 临时使用，直接加入企业，不允许拒绝
def add_company_member(request):
    # 获取通过Token验证的当前用户
    current_user = request.user
    company = request.company_object
    user_to_add = request.user_object

    # 检查当前用户是否为企业成员
    if not CompanyMember.objects.filter(company=company, user=current_user).exists():
        return JsonResponse({"status": "error", "message": "You are not a member of this company"},
                            status=status.HTTP_403_FORBIDDEN)
    # 检查欲添加用户是否已是企业成员
    if CompanyMember.objects.filter(company=company, user=user_to_add).exists():
        return JsonResponse({"status": "error", "message": "User is already a member of this company"},
                            status=status.HTTP_400_BAD_REQUEST)
    # 添加用户到企业
    CompanyMember.objects.create(company=company, user=user_to_add)
    # json_str = json.dumps({
    #     "username": user_to_add.username,
    #     "notification_type": "system",
    #     "content": f"You have been added to the company {company.company_name} by {current_user.username}",
    # })
    # create_notification(json_str)
    return JsonResponse({'status': 'success', "message": "User successfully added to the company"},
                        status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_company
@require_user
def send_join_verification(request):
    # 获取通过Token验证的当前用户
    current_user = request.user
    company = request.company_object
    user_to_add = request.user_object

    # 检查当前用户是否为企业成员
    if not CompanyMember.objects.filter(company=company, user=current_user).exists():
        return JsonResponse({"status": "error", "message": "You are not a member of this company"},
                            status=status.HTTP_403_FORBIDDEN)
    # 检查欲添加用户是否已是企业成员
    if user_to_add.is_staff:
        return JsonResponse({"status": "error", "message": "User is already a member of this company"},
                            status=status.HTTP_400_BAD_REQUEST)
    # 发送加入验证
    JoinVerification.objects.create(company=company, user=user_to_add)
    # json_str = json.dumps({
    #     "username": user_to_add.username,
    #     "notification_type": "system",
    #     "content": f"You have been added to the company {company.company_name} by {current_user.username}",
    # })
    # create_notification(json_str)
    return JsonResponse({'status': 'success', "message": "Join verification successfully send to user"},
                        status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_company
@require_user
def accept_join_verification(request):
    current_user = request.user
    company = request.company_object
    # 用户点击加入企业按扭，发送请求到后端，后端调用此接口，将用户加入企业
    CompanyMember.objects.create(company=company, user=current_user)
    current_user.is_staff = True
    current_user.save()
    return JsonResponse({'status': 'success', "message": "User successfully added to the company"},
                        status=status.HTTP_201_CREATED)
