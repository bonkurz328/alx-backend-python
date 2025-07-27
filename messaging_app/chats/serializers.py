from rest_framework import serializers
from .models import Book
from .models import User, Conversation, Message

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    Handles serialization/deserialization of User instances.
    """
    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'role',
            'created_at'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'created_at': {'read_only': True}
        }
        
class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Message model.
    Includes sender details in the serialized output.
    """
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = [
            'id',
            'sender',
            'message_body',
            'sent_at'
            'conversation', 
            'user', 
            'content', 
            'created_at'
        ]
        read_only_fields = ['id', 'sent_at']

class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Conversation model.
    Includes nested participants and messages.
    """
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = [
            'id',
            'participants',
            'messages',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ConversationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new conversations.
    Handles participant IDs during creation.
    """
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=True
    )


    class Meta:
        model = Conversation
        fields = ['id', 'participant_ids']
        read_only_fields = ['id']

    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids')
        conversation = Conversation.objects.create(**validated_data)
        
        # Add participants to the conversation
        conversation.participants.add(*participant_ids)
        
        return conversation


class MessageCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new messages.
    Handles message creation within conversations.
    """
    class Meta:
        model = Message
        fields = [
            'id',
            'conversation',
            'message_body'
        ]
        read_only_fields = ['id']

    def validate_conversation(self, value):
        """
        Validate that the sender is a participant in the conversation.
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if not value.participants.filter(id=request.user.id).exists():
                raise serializers.ValidationError(
                    "You are not a participant in this conversation."
                )
        return value

