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
from UserManagement.serializers import UserSerializer
from UserManagement.models import User, VerificationCode
from shared.decorators import require_user
from shared.utils.UserManage.users import get_user_by_username, get_user_by_email
from shared.utils.email import send_email
import shutil
import os

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
        print(type(user))
        print(user)
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
        print(verification_code.expires_at)
        print(timezone.now())
        return JsonResponse({"status": "error", "message": "Verification code expired"},
                            status=status.HTTP_401_UNAUTHORIZED)

    if get_user_by_email(email) or get_user_by_username(username):
        return JsonResponse({"status": "error", "message": "User already exists"}, status=status.HTTP_409_CONFLICT)

    hashed_password = make_password(password)
    verification_code.delete()
    new_user = User(password=hashed_password, username=username, real_name=real_name, email=email)
    new_user.save()

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
    print(timezone.now())
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
        print(verification_code.expires_at)
        print(timezone.now())
        return JsonResponse({"status": "error", "message": "Verification code expired"},
                            status=status.HTTP_200_OK)
    user.set_password(data.get('password'))
    user.save()
    return JsonResponse({"status": "success", "message": "Password updated successfully"}, status=status.HTTP_200_OK)



@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_user(request):
    data = request.data  # 获取前端传入的JSON数据

    # 获取通过Token验证的当前用户
    current_user = request.user

    if data.get('password') is not None or data.get('email') is not None:
        verification_code = VerificationCode.objects.filter(email=current_user.email).order_by('-created_at').first()

        if not verification_code or verification_code.code != data.get('code'):
            return JsonResponse({"status": "error", "message": "ERROR CODE"}, status=status.HTTP_401_UNAUTHORIZED)

        if verification_code.expires_at < timezone.now():
            print(verification_code.expires_at)
            print(timezone.now())
            return JsonResponse({"status": "error", "message": "Verification code expired"},
                                status=status.HTTP_401_UNAUTHORIZED)

    # 在这里进行实际的更新操作
    try:
        # 更新密码
        if data.get('password') is not None and not check_password(data.get('password'), current_user.password):
            current_user.set_password(data.get('password'))
        # 更新真实姓名
        if data.get('real_name') is not None and data.get('real_name') != current_user.real_name:
            current_user.real_name = data.get('real_name')
        # 更新邮箱
        if data.get('email') is not None and data.get('email') != current_user.email:
            if get_user_by_email(data.get('email')):
                return JsonResponse({"status": "error", "message": "Email already used"})
            current_user.email = data.get('email')
        # 更新教育经历
        if data.get('education') is not None and data.get('education') != current_user.education:
            current_user.education = data.get('education')
        # 更新期望职位
        if data.get('desired_position') is not None and data.get('desired_position') != current_user.desired_position:
            current_user.desired_position = data.get('desired_position')
        # 更新博客链接
        if data.get('blog_link') is not None and data.get('blog_link') != current_user.blog_link:
            current_user.blog_link = data.get('blog_link')
        # 更新代码仓库链接
        if data.get('repository_link') is not None and data.get('repository_link') != current_user.repository_link:
            current_user.repository_link = data.get('repository_link')
        # 保存更改
        current_user.save()
        return JsonResponse({"status": "success", "message": "Profile updated successfully"}, status=status.HTTP_200_OK)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        query = Q(username__icontains=keyword) | Q(real_name__icontains=keyword) | \
                Q(education__icontains=keyword) | Q(desired_position__icontains=keyword)
        users = User.objects.filter(query)
    else:
        # 如果没有提供关键词，则返回所有用户
        users = User.objects.all()

    # 将用户数据转换为 JSON 格式并返回
    user_data = [{
        "username": user.username,
        "real_name": user.real_name,
        "education": user.education,
        "desired_position": user.desired_position,
        "blog_link": user.blog_link,
        "repository_link": user.repository_link
    } for user in users]

    return JsonResponse(user_data, safe=False)
# def search_users(keyword):
#     with connection.cursor() as cursor:
#         # 明确指定查询字段，这些字段需要与 User 模型的字段一致
#         sql = """
#         SELECT username, real_name, education, desired_position, blog_link, repository_link
#         FROM Users
#         WHERE MATCH(real_name, desired_position) AGAINST(%s IN NATURAL LANGUAGE MODE)
#         """
#         cursor.execute(sql, [keyword])
#         result_list = cursor.fetchall()
#
#     # 创建 User 模型实例
#     # 确保查询返回的列顺序与下面的顺序一致
#     users = [User(username=row[0], real_name=row[1], education=row[2], desired_position=row[3], blog_link=row[4], repository_link=row[5]) for row in result_list]
#     return users


# @csrf_exempt
# @api_view(['PUT'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
# def set_user_avatar(request):
#     try:
#         # 从请求中获取文件
#         avatar = request.FILES.get('avatar', None)
#         if not avatar:
#             return JsonResponse({"status": "error", "message": "No avatar file provided"},
#                                 status=status.HTTP_400_BAD_REQUEST)
#         # 获取用户
#         user = User.objects.get(username=request.user.username)
#         # 删除旧的头像文件，如果存在的话
#         if user.avatar:
#             with Lock(user.avatar.path, 'r+b'):
#                 user.avatar.delete(save=False)
#         # 创建新的头像文件名
#         new_filename = f"{user.username}_avatar.png"
#         # 读取和保存新文件
#         new_file = ContentFile(avatar.read())
#         new_file.name = new_filename
#         # 保存新的头像
#         user.avatar.save(new_filename, new_file, save=True)
#     except Exception as e:
#         return JsonResponse({"status": "error", "message": f"An error occurred: {str(e)}"},
#                             status=status.HTTP_400_BAD_REQUEST)
#     return JsonResponse({"status": "success", "message": "Avatar updated successfully"}, status=status.HTTP_200_OK)


