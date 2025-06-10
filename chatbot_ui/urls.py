from django.urls import path
from . import views

urlpatterns = [
    path('send_message/', views.send_message, name='send_message'),
    path('get_conversation/<int:conversation_id>/', views.get_conversation, name='get_conversation'),
    path('', views.chat, name='chat'),
    path('<int:conversation_id>/', views.chat, name='chat_conversation'),
] 