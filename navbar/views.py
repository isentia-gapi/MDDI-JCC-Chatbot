from django.shortcuts import render
from chatbot_ui.models import Conversation

# Create your views here.

def navbar(request):
    context = {}
    if request.user.is_authenticated:
        context['conversations'] = Conversation.objects.filter(user=request.user).order_by('-updated_at')
    return render(request, 'navbar/navbar.html', context)
