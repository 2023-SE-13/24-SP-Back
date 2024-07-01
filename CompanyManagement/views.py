import json
from django.core.files.base import ContentFile
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from portalocker import Lock

from CompanyManagement.serializer import CompanySerializer, CompanyMemberUserSerializer
from UserManagement.models import User
from CompanyManagement.models import JoinVerification, CompanyMember, Company
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
    current_user = request.user
    company_name = data.get('company_name')
    company_description = data.get('company_description')
    if current_user.is_staff:
        return JsonResponse({"status": "error", "message": "You are already a member of a company"},
                            status=status.HTTP_400_BAD_REQUEST)
    if not company_name or not company_description:
        return JsonResponse(
            {"status": "error", "message": "company_name, company_description are required"},
            status=status.HTTP_406_NOT_ACCEPTABLE)

    company = Company.objects.filter(company_name=company_name)
    if company.exists():
        return JsonResponse({"status": "error", "message": "Company name already exists"},
                            status=status.HTTP_409_CONFLICT)

    company = Company(company_name=company_name, company_description=company_description)
    company.save()
    # 设置默认image
    default_image_path = 'resources/company_images/default_image.png'
    with open(default_image_path, 'rb') as f:
        image_content = f.read()
    new_filename = f"{company.company_id}_image.png"
    new_file = ContentFile(image_content)
    new_file.name = new_filename
    company.company_image.save(new_filename, new_file, save=True)

    # 将创建者加入Company
    user = request.user
    company_member = CompanyMember(company=company, user=user, role='Admin')
    company_member.save()
    user.is_staff = True
    user.save()
    return JsonResponse({'status': 'success'}, status=status.HTTP_201_CREATED)


@api_view(['PUT'])
@csrf_exempt
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_company(request):
    data = json.loads(request.body.decode('utf-8'))
    cur_user = request.user
    cm = CompanyMember.objects.filter(user=cur_user).first()
    if cm is None or cm.role == 'Staff':
        return JsonResponse({"status": "error", "message": "You are not allowed to update company"},
                            status=status.HTTP_400_BAD_REQUEST)
    company = cm.company
    fields_to_update = ['company_name', 'company_description']
    for field in fields_to_update:
        if field in data:
            setattr(company, field, data[field])
    company.save()
    return JsonResponse({'status': 'success'}, status=status.HTTP_201_CREATED)

@api_view(['PUT'])
@csrf_exempt
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_logo(request):
    cur_user = request.user
    cm = CompanyMember.objects.filter(user=cur_user).first()
    if cm is None or cm.role == 'Staff':
        return JsonResponse({"status": "error", "message": "You are not allowed to update company logo"},
                            status=status.HTTP_400_BAD_REQUEST)
    company = cm.company
    logo = request.FILES.get('logo')
    if logo is None:
        return JsonResponse({"status": "error", "message": "company_image is required"},
                            status=status.HTTP_400_BAD_REQUEST)

    if company.company_image:
        with Lock(company.company_image.path, 'r+b'):
            company.company_image.delete(save=False)
    new_filename = f"{company.company_id}_image.png"
    new_file = ContentFile(logo.read())
    new_file.name = new_filename
    company.company_image.save(new_filename, new_file, save=True)
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
    user_to_add.is_staff = True
    return JsonResponse({'status': 'success', "message": "User successfully added to the company"},
                        status=status.HTTP_201_CREATED)

@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_company
@require_user
def delete_staff(request):
    current_user = request.user
    company = request.company_object
    if CompanyMember.objects.get(company=company, user=current_user).role != 'Admin':
        return JsonResponse({"status": "error", "message": "You have no permission to delete staff"},
                            status=status.HTTP_400_BAD_REQUEST)
    user_to_delete = request.user_object
    if CompanyMember.objects.filter(company=company, user=user_to_delete).exists():
        CompanyMember.objects.get(company=company, user=user_to_delete).delete()
        user_to_delete.is_staff = False
        user_to_delete.save()
        return JsonResponse({'status': 'success', "message": "User successfully deleted from the company"},
                            status=status.HTTP_200_OK)


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
    return JsonResponse({'status': 'success', "message": "Join verification successfully send to user"},
                        status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_company
def accept_join_verification(request):
    current_user = request.user
    company = request.company_object
    # 用户点击加入企业按扭，发送请求到后端，后端调用此接口，将用户加入企业
    CompanyMember.objects.create(company=company, user=current_user)
    current_user.is_staff = True
    current_user.save()
    try:
        # 用户同意后删除加入验证
        JoinVerification.objects.get(company=company, user=current_user).delete()
    except JoinVerification.DoesNotExist:
        return JsonResponse({'status': 'fail', 'message': 'Join verification not found'}, status=404)
    return JsonResponse({'status': 'success', "message": "User successfully added to the company"},
                        status=status.HTTP_201_CREATED)


@api_view(["POST"])
@csrf_exempt
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_company
def leave_company(request):
    if request.method == 'POST':
        # 尝试从请求体中读取JSON数据
        try:
            company = request.company_object
            user = request.user
            # 尝试获取company-member对象
            try:
                member = CompanyMember.objects.get(company=company, user=user)
                if member.role != 'Admin':
                    # 如果找到了，则删除
                    member.delete()
                    user.is_staff = 0  # 或者如果is_staff是布尔字段，可以使用 user_manage_obj.is_staff = False
                    user.save()  # 保存更改
                # 返回成功的响应
                else:
                    return JsonResponse({'status': 'fail', 'message': 'You are Admin!'}, status=405)
                return JsonResponse({'status': 'success'})
            except CompanyMember.DoesNotExist:
                # 如果没有找到，则返回失败的响应
                return JsonResponse({'status': 'fail', 'message': 'Member not found'}, status=404)
        except json.JSONDecodeError:
            # 如果JSON解析失败，返回错误响应
            return JsonResponse({'status': 'fail', 'message': 'Invalid JSON data'}, status=400)
            # 如果不是POST请求，返回错误响应
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@csrf_exempt
@api_view(['GET'])
@require_company
def get_company(request):
    cp = request.company_object
    serializer = CompanySerializer(cp)
    return JsonResponse({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
def search_company(request):
    data = json.loads(request.body.decode('utf-8'))
    keywords = data.get('keywords', None).split()
    query = Q()
    if not keywords:
        return JsonResponse({"status": "error", "message": "keyword is required"}, status=status.HTTP_400_BAD_REQUEST)

    for keyword in keywords:
        for field in ['company_name', 'company_description']:
            query |= Q(**{f'{field}__icontains': keyword})
    results = Company.objects.filter(query).values()
    return JsonResponse({"status": "success", "data": CompanySerializer(results, many=True).data},
                        status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
@require_company
def get_staff(request):
    company = request.company_object
    staff = CompanyMember.objects.filter(company=company)
    return JsonResponse({"status": "success", "data": CompanyMemberUserSerializer(staff, many=True).data},
                        status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
@require_company
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def is_staff(request):
    company = request.company_object
    user = request.user
    if CompanyMember.objects.filter(company=company, user=user).exists():
        return JsonResponse({"status": "success"}, status=status.HTTP_200_OK)
    else:
        return JsonResponse({"status": "error"}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
@require_company
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def is_to_join(request):
    company = request.company_object
    user = request.user
    if JoinVerification.objects.filter(company=company, user=user).exists():
        return JsonResponse({"status": "y"}, status=status.HTTP_200_OK)
    else:
        return JsonResponse({"status": "n"}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
@require_company
@require_user
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def transfer_admin(request):
    company = request.company_object
    admin_user = request.user
    user_to_transfer = request.user_object
    company_member = CompanyMember.objects.filter(company=company, user=user_to_transfer).first()
    if company_member:
        if company_member.role == 'Staff':
            # 完美符合，可以转让
            to_transfer = CompanyMember.objects.get(company=company, user=admin_user)
            to_transfer.role = 'Staff'
            to_transfer.save()
            company_member.role = 'Admin'
            company_member.save()
            return JsonResponse({"status": "success"}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({"status": "error", "message": "Target user's is not a staff"},
                                status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({"status": "error", "message": "Target user is not a member of this company"},
                            status=status.HTTP_404_NOT_FOUND)


