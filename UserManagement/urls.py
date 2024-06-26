from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 创建一个 router 并注册 ViewSet
router = DefaultRouter()
router.register(r'users', views.UserCURDViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login', views.login),
    path('logout', views.logout),
    path('register', views.register),
    path('verification', views.get_verification_code),
    path('get_user', views.get_user),
    path('update_user', views.update_user),
    path('forget_password', views.forget_password),
    path('search_users', views.search_users)

]
