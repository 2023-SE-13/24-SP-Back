from django.urls import path
from PositionManagement.views import create_position, get_position, delete_position, get_position_list

urlpatterns = [
    path('create_position', create_position),
    path('get_position', get_position),
    path('delete_position', delete_position),
    path('get_position_list', get_position_list)]
