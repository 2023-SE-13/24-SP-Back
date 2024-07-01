
from django.urls import path, include
from rest_framework.routers import DefaultRouter


# 创建一个 router 并注册 ViewSet
from CompanyManagement.views import *

# router = DefaultRouter()
# router.register(r'companys', CompanyCURDViewSet)
# router.register(r'company_members', CompanyMemberCURDViewSet)

urlpatterns = [
    # path('', include(router.urls)),
    path('create_company', create_company),
    path('send_join_verification', send_join_verification),
    path('accept_join_verification', accept_join_verification),
    path('leave_company', leave_company),
    path('get_company', get_company),
    path('get_staff', get_staff),
    path('search_company', search_company),
    path('is_staff', is_staff),
    path('is_to_join', is_to_join),
    path('add_staff', add_company_member),
    path('update_company', update_company),
    path('transfer_admin', transfer_admin),
]
