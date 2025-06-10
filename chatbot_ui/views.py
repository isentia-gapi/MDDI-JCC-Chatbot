from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Conversation, Message
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json

# Create your views here.

@login_required
def chat(request, conversation_id=None):
    conversations = Conversation.objects.filter(user=request.user).order_by('-updated_at')
    if conversation_id:
        conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
        messages = conversation.messages.all()
    else:
        conversation = None
        messages = []
    return render(request, 'chatbot_ui/chat.html', {
        'conversations': conversations,
        'conversation': conversation,
        'messages': messages,
    })

@csrf_exempt
def send_message(request):
    if request.method == 'POST' and request.user.is_authenticated:
        data = json.loads(request.body)
        message_text = data.get('message')
        conversation_id = data.get('conversation_id')

        # Get or create conversation
        if conversation_id:
            conversation = Conversation.objects.get(id=conversation_id, user=request.user)
        else:
            conversation = Conversation.objects.create(
                user=request.user,
                title=f"Conversation {Conversation.objects.filter(user=request.user).count() + 1}"
            )

        # Save user message
        user_msg = Message.objects.create(
            conversation=conversation,
            content=message_text,
            is_user=True,
            timestamp=timezone.now()
        )

        # Call Cloud Run function
        cloud_run_url = 'https://mddi-jcc-daily-report-chatbot-88965502560.asia-east1.run.app'  # Replace with your actual URL
        payload = {
            'message': message_text,
            'thread_id': str(conversation.id)
        }
        try:
            response = requests.post(cloud_run_url, json=payload)
            response_data = response.json()
            bot_reply = response_data.get('reply', 'No response from AI.')
        except Exception as e:
            bot_reply = f"Error: {str(e)}"

        # Save bot message
        Message.objects.create(
            conversation=conversation,
            content=bot_reply,
            is_user=False,
            timestamp=timezone.now()
        )

        conversation.updated_at = timezone.now()
        conversation.save()

        return JsonResponse({
            'reply': bot_reply,
            'conversation_id': conversation.id
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)

def get_conversation(request, conversation_id):
    if request.user.is_authenticated:
        conversation = Conversation.objects.get(id=conversation_id, user=request.user)
        messages = conversation.messages.all()
        messages_data = [
            {
                'content': msg.content,
                'is_user': msg.is_user,
                'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }
            for msg in messages
        ]
        return JsonResponse({'messages': messages_data})
    return JsonResponse({'error': 'Unauthorized'}, status=403)
