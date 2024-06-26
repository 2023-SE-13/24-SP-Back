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
    path('unsubscribe_company', views.unsubscribe_company, name='unsubscribe_company'),
    path('unsubscribe_user', views.unsubscribe_user, name='unsubscribe_user'),
    path('do_subscribed_company', views.do_subscribed_company, name='do_subscribed_company'),
    path('do_subscribed_user', views.do_subscribed_user, name='do_subscribed_user'),
]