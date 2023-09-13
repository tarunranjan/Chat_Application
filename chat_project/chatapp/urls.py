from django.urls import path
from .views import (
    user_registration,
    user_login,
    get_online_users,
    start_chat,
    send_message,
    suggested_friends,
)

urlpatterns = [
    path('register/', user_registration, name='user_registration'),
    path('login/', user_login, name='user_login'),
    path('online-users/', get_online_users, name='get_online_users'),
    path('chat/start/', start_chat, name='start_chat'),
    path('chat/send/', send_message, name='send_message'),
    path('suggested-friends/<int:user_id>/', suggested_friends, name='suggested_friends'),
]
