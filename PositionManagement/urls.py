from django.urls import path
from PositionManagement.views import *

urlpatterns = [
    path('create_position', create_position),
    path('get_position', get_position),
    path('delete_position', delete_position),
    path('get_position_list', get_position_list),
    path('apply_position', apply_position),
    path('get_pos_apy', get_position_applications),
    path('update_position', update_position),
    path('create_offer', create_offer),
    path('get_offer', get_offer),
    path('get_offer_list', get_offer_list),
    path('update_offer', update_offer),
    path('refuse_application', refuse_application),
]
