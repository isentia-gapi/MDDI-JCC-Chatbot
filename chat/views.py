from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from .models import Conversation

@login_required
def chat_view(request):
    conversations = Conversation.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'chat/chat.html', {'conversations': conversations})

@login_required
def chat_conversation(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    conversations = Conversation.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'chat/chat.html', {
        'conversation': conversation,
        'conversations': conversations
    })

@login_required
@require_POST
def rename_conversation(request, conversation_id):
    try:
        data = json.loads(request.body)
        new_title = data.get('title')
        
        if not new_title:
            return JsonResponse({'success': False, 'error': 'Title is required'})
            
        conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
        conversation.title = new_title
        conversation.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}) 