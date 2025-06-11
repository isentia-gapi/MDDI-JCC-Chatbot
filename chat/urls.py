from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('conversation/<int:conversation_id>/', views.chat_conversation, name='chat_conversation'),
    path('delete/<int:conversation_id>/', views.delete_conversation, name='delete_conversation'),
] 