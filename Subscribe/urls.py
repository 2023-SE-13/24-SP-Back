from django.urls import path
from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'subscribe_companys', views.Subscribe_companyCURDViewSet)
router.register(r'subscribe_users', views.Subscribe_userCURDViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('subscribe_company', views.subscribe_company, name='subscribe_company'),
    path('subscribe_user', views.subscribe_user, name='subscribe_user'),
]