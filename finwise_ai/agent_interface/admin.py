from django.contrib import admin

from .models import (
    Conversation,
    Message,
    PromptTemplate,
    UserQuery,
    AgentAction,
)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "created_at", "is_archived")
    search_fields = ("title", "user__email")
    list_filter = ("is_archived",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("conversation", "message_type", "created_at")
    list_filter = ("message_type", "created_at")


@admin.register(PromptTemplate)
class PromptTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name",)


@admin.register(UserQuery)
class UserQueryAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "conversation",
        "detected_intent",
        "confidence_score",
        "processed_successfully",
    )
    list_filter = ("detected_intent", "processed_successfully")
    search_fields = ("query_text", "user__email")


@admin.register(AgentAction)
class AgentActionAdmin(admin.ModelAdmin):
    list_display = ("user_query", "action_type", "status", "created_at")
    list_filter = ("action_type", "status")
