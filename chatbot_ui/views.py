from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Conversation, Message
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
from .bot import ChatBot

# Create your views here.

# Initialize the bot
chatbot = ChatBot()

@login_required
def chat(request, conversation_id=None):
    conversations = Conversation.objects.filter(user=request.user).order_by('-updated_at')
    
    if conversation_id:
        try:
            conversation = Conversation.objects.get(id=conversation_id, user=request.user)
            messages = conversation.messages.all().order_by('timestamp')
        except Conversation.DoesNotExist:
            # If conversation doesn't exist, create a new one
            conversation = Conversation.objects.create(
                user=request.user,
                title=f"Conversation {Conversation.objects.filter(user=request.user).count() + 1}"
            )
            messages = []
    else:
        # If no conversation_id is provided, create a new conversation
        conversation = Conversation.objects.create(
            user=request.user,
            title=f"Conversation {Conversation.objects.filter(user=request.user).count() + 1}"
        )
        messages = []
    
    return render(request, 'chatbot_ui/chat.html', {
        'conversations': conversations,
        'conversation': conversation,
        'messages': messages,
    })

@csrf_exempt
def send_message(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
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

            # Get bot response
            bot_reply = chatbot.get_response(message_text, str(conversation.id))

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
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
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

@login_required
def new_conversation(request):
    # Create a new conversation
    conversation = Conversation.objects.create(
        user=request.user,
        title=f"Conversation {Conversation.objects.filter(user=request.user).count() + 1}"
    )
    # Redirect to the chat view with the new conversation
    return redirect('chat_conversation', conversation_id=conversation.id)

@csrf_exempt
@login_required
def delete_conversation(request, conversation_id):
    if request.method == 'POST':
        try:
            conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
            conversation.delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def home(request):
    return render(request, 'chatbot_ui/home.html')
