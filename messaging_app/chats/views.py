from rest_framework import generics
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import MyModel
from .models import Conversation, Message
from .permissions import IsParticipantOfConversation
from .filters import MessageFilter
from .serializers import (
    ConversationSerializer,
    ConversationCreateSerializer,
    MessageSerializer,
    MessageCreateSerializer,
    MyModelSerializer
)



class BookListCreateAPIView(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Conversation operations.
    Supports listing conversations and creating new ones.
    """
    queryset = Conversation.objects.all()
    permission_classes = [IsAuthenticated] 
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    def get_queryset(self):
        # Only return conversations where the user is a participant
        return Conversation.objects.filter(participants=self.request.user)

    def get_serializer_class(self):
        """
        Returns appropriate serializer based on action.
        """
        if self.action == 'create':
            return ConversationCreateSerializer
        return ConversationSerializer

    def get_queryset(self):
        """
        Returns conversations where the current user is a participant.
        """
        return self.queryset.filter(participants=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Create a new conversation with participants.
        Automatically adds the current user as a participant.
        """
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get participant IDs and add current user if not already included
        participant_ids = serializer.validated_data['participant_ids']
        if request.user.id not in participant_ids:
            participant_ids.append(request.user.id)
        
        # Create conversation with participants
        conversation = Conversation.objects.create()
        conversation.participants.add(*participant_ids)
        
        # Return the created conversation
        response_serializer = ConversationSerializer(conversation)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Message operations.
    Supports listing messages in a conversation and creating new messages.
    """
    queryset = Message.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filterset_class = MessageFilter

    def get_serializer_class(self):
        """
        Returns appropriate serializer based on action.
        """
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer

    def get_queryset(self):
        """
        Returns messages from conversations where the current user is a participant.
        """
        return self.queryset.filter(
            conversation__participants=self.request.user
        ).order_by('sent_at')
        return Message.objects.filter(conversation__participants=self.request.user).order_by('-created_at') 

    def create(self, request, *args, **kwargs):
        """
        Create a new message in a conversation.
        Automatically sets the sender to the current user.
        """
        serializer = self.get_serializer_class()(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        # Create message with current user as sender
        message = Message.objects.create(
            sender=request.user,
            conversation=serializer.validated_data['conversation'],
            message_body=serializer.validated_data['message_body']
        )
        
        # Return the created message
        response_serializer = MessageSerializer(message)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

