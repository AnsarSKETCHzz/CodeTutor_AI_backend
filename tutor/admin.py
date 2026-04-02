from django.contrib import admin
from .models import ConversationLog

@admin.register(ConversationLog)
class ConversationLogAdmin(admin.ModelAdmin):
    list_display = ('mode', 'created_at', 'short_input')
    list_filter = ('mode', 'created_at')
    search_fields = ('user_input', 'ai_response')
    readonly_fields = ('mode', 'user_input', 'ai_response', 'created_at')

    def short_input(self, obj):
        return obj.user_input[:80] + '...' if len(obj.user_input) > 80 else obj.user_input
    short_input.short_description = 'Input Preview'
