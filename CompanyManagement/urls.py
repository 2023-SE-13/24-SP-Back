
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

# 创建一个 router 并注册 ViewSet
router = DefaultRouter()
router.register(r'companys', CompanyCURDViewSet)
router.register(r'company_members', CompanyMemberCURDViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('create_company', create_company),
    path('send_join_verification', send_join_verification),
    path('accept_join_verification', accept_join_verification),
    path('leave_company', leave_company),
    # path('remove_company_member', remove_company_member),
    # path('get_member_role', get_user_role_in_company),
    # path('set_member_role', set_company_member_role),
    # path('get_company_members', get_company_members),
    # path('get_companys', get_user_companys),
    # path('get_company', get_company),
    # path('set_company_image', set_company_image),
    #
    # path('create_public_group', chat_views.create_public_group),
    # path('create_private_chat', chat_views.create_private_chat),
    # path('save_message', chat_views.save_message),
    # path('get_group', chat_views.get_group),
    # path('get_user_groups', chat_views.get_user_groups),
    # path('get_messages', chat_views.get_group_messages),
    # path('get_group_members', chat_views.get_group_members),
    # path('delete_group', chat_views.delete_group),
    # path('add_group_member', chat_views.add_group_member),
    # path('remove_group_member', chat_views.remove_group_member),
    # path('get_user_role_in_group', chat_views.get_user_role_in_group),
]
