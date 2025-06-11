from .models import Conversation

def conversations(request):
    if request.user.is_authenticated:
        return {
            'conversations': Conversation.objects.filter(user=request.user).order_by('-updated_at')
        }
    return {'conversations': []} 