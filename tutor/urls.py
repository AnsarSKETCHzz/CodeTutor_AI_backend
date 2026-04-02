from django.urls import path
from .views import DebugView, ExplainView, ChatView

urlpatterns = [
    path('debug/', DebugView.as_view(), name='debug'),
    path('explain/', ExplainView.as_view(), name='explain'),
    path('chat/', ChatView.as_view(), name='chat'),
]
