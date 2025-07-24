pythonCopy codefrom django.urls import path
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet
from .views import BookListCreateAPIView


# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path("api/books", views.BookListCreateAPIView.as_view(), name="book_list_create"),
    path('', include(router.urls)),
]
