from django.urls import path, include
from PositionManagement.views import *


path('create_position', create_position),
path('get_position', get_position),
path('delete_position', delete_position),
path('get_position_list', get_position_list),