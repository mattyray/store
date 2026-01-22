"""
URL patterns for the chat app.
"""
from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # SSE streaming chat endpoint
    path('', views.chat_stream, name='chat_stream'),

    # Sync chat endpoint (for testing)
    path('sync/', views.chat_sync, name='chat_sync'),

    # Get conversation history
    path('history/<uuid:conversation_id>/', views.chat_history, name='chat_history'),

    # Upload image for chat
    path('upload-image/', views.upload_chat_image, name='upload_chat_image'),
]
