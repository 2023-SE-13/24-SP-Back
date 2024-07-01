from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.db import connection
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.hashers import check_password, make_password
from django.db.models import Q
from portalocker import Lock
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework import viewsets, status
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
import random
import json

from CompanyManagement.models import CompanyMember
from UserManagement.serializers import UserSerializer
from UserManagement.models import User, VerificationCode, Skill, PositionTag
from shared.decorators import require_user
from shared.utils.UserManage.users import get_user_by_username, get_user_by_email
from shared.utils.email import send_email

from shared.utils.UserManage.users import get_user_by_email


class UserCURDViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = User.objects.all()
    serializer_class = UserSerializer


@api_view(['POST'])
@csrf_exempt
def login(request):
    data = json.loads(request.body.decode('utf-8'))

    username = data.get('username')
    password = data.get('password')

    try:
        user = User.objects.get(username=username)
        if check_password(password, user.password):
            token, created = Token.objects.get_or_create(user=user)
            return JsonResponse({"status": "success", "token": str(token.key)}, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse({"status": "wrong password"}, status=status.HTTP_401_UNAUTHORIZED)
    except User.DoesNotExist:
        return JsonResponse({"status": "user does not exist"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@csrf_exempt
def register(request):
    data = json.loads(request.body.decode('utf-8'))
    username = data.get('username')
    password = data.get('password')
    real_name = data.get('real_name')
    email = data.get('email')
    code = data.get('code')

    if not password or not email or not code or not username or not real_name:
        return JsonResponse({"status": "error", "message": "ALL messages are required"},
                            status=status.HTTP_400_BAD_REQUEST)

    verification_code = VerificationCode.objects.filter(email=email).order_by('-created_at').first()

    if not verification_code or verification_code.code != code:
        return JsonResponse({"status": "error", "message": "ERROR CODE"}, status=status.HTTP_401_UNAUTHORIZED)

    if verification_code.expires_at < timezone.now():
        return JsonResponse({"status": "error", "message": "Verification code expired"},
                            status=status.HTTP_401_UNAUTHORIZED)

    if get_user_by_username(username):
        return JsonResponse({"status": "error", "message": "User already exists"}, status=status.HTTP_409_CONFLICT)

    hashed_password = make_password(password)
    verification_code.delete()
    new_user = User(password=hashed_password, username=username, real_name=real_name, email=email)
    new_user.save()

    default_avatar_path = 'resources/avatars/default_avatar.png'
    with open(default_avatar_path, 'rb') as f:
        avatar_content = f.read()
    new_filename = f"{username}_avatar.png"
    new_file = ContentFile(avatar_content)
    new_file.name = new_filename
    new_user.avatar.save(new_filename, new_file, save=True)

    return JsonResponse({"status": "success", "message": "User successfully registered"},
                        status=status.HTTP_200_OK)


@api_view(['POST'])
@csrf_exempt
def get_verification_code(request):
    email = request.GET.get('email')

    if not email:
        return JsonResponse({"status": "error", "message": "email is required"}, status=status.HTTP_400_BAD_REQUEST)

    code = str(random.randint(1000, 9999))

    # 保存验证码
    VerificationCode.objects.create(email=email, code=code)
    # 在这里添加发送邮件的代码
    send_email(email, code)

    return JsonResponse({"status": "success", "message": "Verification code sent"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@csrf_exempt
def logout(request):
    try:
        # 获取当前用户的Token
        token = Token.objects.get(user=request.user)
        # 删除Token
        token.delete()
        return JsonResponse({"status": "success", "message": "Successfully logged out."}, status=status.HTTP_200_OK)
    except Token.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Token not found."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@require_user
@csrf_exempt
def forget_password(request):
    user = request.user_object
    data = request.data
    if not data.get('password') or not data.get('code'):
        return JsonResponse({"status": "error", "message": "Password and code are required"}, status=status.HTTP_200_OK)
    verification_code = VerificationCode.objects.filter(email=user.email).order_by('-created_at').first()

    if not verification_code or verification_code.code != data.get('code'):
        return JsonResponse({"status": "error", "message": "ERROR CODE"}, status=status.HTTP_200_OK)

    if verification_code.expires_at < timezone.now():
        return JsonResponse({"status": "error", "message": "Verification code expired"},
                            status=status.HTTP_200_OK)
    user.set_password(data.get('password'))
    user.save()
    return JsonResponse({"status": "success", "message": "Password updated successfully"}, status=status.HTTP_200_OK)

@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_user(request):
    data = request.data
    current_user = User.objects.get(username=request.user.username)

    if 'password' in data or 'email' in data:
        if not validate_verification_code(current_user.email, data.get('code')):
            return JsonResponse({"status": "error", "message": "ERROR CODE"}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        update_user_fields(current_user, data)
        update_user_relationships(current_user, data)
        current_user.save()
        return JsonResponse({"status": "success", "message": "Profile updated successfully"}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def validate_verification_code(email, code):
    verification_code = VerificationCode.objects.filter(email=email).order_by('-created_at').first()
    if not verification_code or verification_code.code != code:
        return False
    if verification_code.expires_at < timezone.now():
        return JsonResponse({"status": "error", "message": "Verification code expired"},
                            status=status.HTTP_401_UNAUTHORIZED)
    return True

def update_user_fields(user, data):
    fields_to_update = [
        'password', 'real_name', 'email', 'education', 'blog_link',
        'repository_link', 'desired_work_city', 'salary_min', 'salary_max',
        'years_of_service', 'cur_position', 'school', 'age'
    ]
    for field in fields_to_update:
        if field in data and getattr(user, field) != data[field]:
            setattr(user, field, data[field])

def update_user_relationships(user, data):
    if 'skills' in data:
        user.skills.clear()
        for skill in data['skills']:
            user.skills.add(Skill.objects.get(name=skill))
    if 'desired_position' in data:
        user.desired_position.clear()
        for positiontag in data['desired_position']:
            user.desired_position.add(
                PositionTag.objects.get(
                    category=positiontag.get('category'),
                    specialization=positiontag.get('specialization')
                )
            )


@csrf_exempt
@api_view(['GET'])
@require_user
def get_user(request):
    user = request.user_object
    serializer = UserSerializer(user)
    return JsonResponse({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
def search_users(request):
    keyword = request.GET.get('keyword')
    if keyword:
        # 创建查询条件，搜索多个字段
        query = Q(username__icontains=keyword)  | \
                Q(education__icontains=keyword)
        users = User.objects.filter(query)
    else:
        # 如果没有提供关键词，则返回所有用户
        users = User.objects.all()
    user_data = []
    for user in users:
        company_member = CompanyMember.objects.filter(user=user).first()
        company_name = company_member.company.company_name if company_member else ""
        # 将用户数据转换为 JSON 格式并返回
        user_data.append({
            "username": user.username,
            "real_name": user.real_name,
            "education": user.education,
            "blog_link": user.blog_link,
            "repository_link": user.repository_link,
            "company_name": company_name
        })

    return JsonResponse(user_data, safe=False)


@csrf_exempt
@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def upload_resume(request):
    try:
        # 从请求中获取文件
        resume = request.FILES.get('resume', None)
        if not resume:
            return JsonResponse({"status": "error", "message": "No resume file provided"},
                                status=status.HTTP_400_BAD_REQUEST)
        # 获取用户
        user = User.objects.get(username=request.user.username)
        # 删除旧的简历文件，如果存在的话
        try:
            if user.resume:
                with Lock(user.resume.path, 'r+b'):
                    user.resume.delete(save=False)
        except Exception:
            pass

        # 创建新的简历文件名
        new_filename = f"{user.username}_resume.pdf"
        # 读取和保存新文件
        new_file = ContentFile(resume.read())
        new_file.name = new_filename
        # 保存新的简历
        user.resume.save(new_filename, new_file, save=True)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"An error occurred: {str(e)}"},
                            status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse({"status": "success", "message": "Resume uploaded successfully"}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def set_avatar(request):
    try:
        # 从请求中获取文件
        avatar = request.FILES.get('avatar', None)
        if not avatar:
            return JsonResponse({"status": "error", "message": "No avatar file provided"},
                                status=status.HTTP_400_BAD_REQUEST)
        # 获取用户
        user = User.objects.get(username=request.user.username)
        # 删除旧的头像文件，如果存在的话
        if user.avatar:
            with Lock(user.avatar.path, 'r+b'):
                user.avatar.delete(save=False)
        # 创建新的头像文件名
        new_filename = f"{user.username}_avatar.png"
        # 读取和保存新文件
        new_file = ContentFile(avatar.read())
        new_file.name = new_filename
        # 保存新的头像
        user.avatar.save(new_filename, new_file, save=True)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"An error occurred: {str(e)}"},
                            status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse({"status": "success", "message": "Avatar updated successfully"}, status=status.HTTP_200_OK)
