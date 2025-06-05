from django.contrib import admin

from .models import Dashboard, DashboardWidget, Notification, FinancialInsight


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")
    search_fields = ("user__email",)


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ("dashboard", "widget_type", "title", "position", "is_enabled")
    list_filter = ("widget_type", "is_enabled")
    search_fields = ("title",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "notification_type", "created_at", "is_read")
    list_filter = ("notification_type", "is_read")
    search_fields = ("title", "user__email")


@admin.register(FinancialInsight)
class FinancialInsightAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "category", "importance_score")
    list_filter = ("category",)
    search_fields = ("title", "user__email")
