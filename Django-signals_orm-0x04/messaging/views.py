from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib import messages
from django.views.generic import DetailView
from .models import Message

@login_required
def delete_user(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, "Your account has been successfully deleted.")
        return redirect(reverse('home'))  # Redirect to home or login page
    return redirect(reverse('profile'))  # Redirect to profile if not POST

class MessageDetailView(DetailView):
    model = Message
    template_name = 'messaging/message_detail.html'
    context_object_name = 'message'

    def get_object(self, queryset=None):
        # Optimize query with prefetch_related for replies and select_related for sender/receiver
        return Message.objects.select_related('sender', 'receiver').prefetch_related('replies').get(pk=self.kwargs['pk'])


