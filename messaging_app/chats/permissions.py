from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions are only allowed to the owner of the message/conversation
        return obj.user == request.user

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to access messages.
    """
    def has_permission(self, request, view):
        # Only allow authenticated users
        if not request.user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        # Check if the object is a Message
        if hasattr(obj, 'conversation'):
            # Allow access if user is a participant in the conversation
            return obj.conversation.participants.filter(id=request.user.id).exists()
        # If object is a Conversation, check participants directly
        return obj.participants.filter(id=request.user.id).exists()
