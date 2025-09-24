from django.urls import path
from .views import DocumentUploadView, ChatStreamView, AsyncChatStreamView

urlpatterns = [
    path('upload/', DocumentUploadView.as_view(), name='upload_document'),
    path("chat/", ChatStreamView.as_view(), name="chat"),
    path("chat/stream/", AsyncChatStreamView.as_view(), name="chat-stream"),
]

