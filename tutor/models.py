from django.db import models

class ConversationLog(models.Model):
    MODE_CHOICES = [
        ('debug', 'Debug'),
        ('explain', 'Explain'),
        ('chat', 'Chat'),
    ]

    mode = models.CharField(max_length=10, choices=MODE_CHOICES)
    user_input = models.TextField()
    ai_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.mode.upper()}] {self.created_at.strftime('%Y-%m-%d %H:%M')}"
