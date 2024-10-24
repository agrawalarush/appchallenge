from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('room/<str:room_name>/', views.chat_room, name='chat_room'),
    path('room/<str:room_name>/send/', views.send_message, name='send_message'),
    path('room/', views.what_room),
    path('room/approve/<str:room_name>/', views.approve_user, name='chat_room'), # ONLY DURRING DEBUGGING!!!
    path('room/remove/<str:room_name>/', views.remove_user, name='chat_room'), # ONLY DURRING DEBUGGING!!!
    path("", views.delete_rooms),
]
