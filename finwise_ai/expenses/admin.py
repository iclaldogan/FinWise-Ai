from django.contrib import admin

from .models import (
    ExpenseCategory,
    Expense,
    RecurringExpense,
    AnomalyDetection,
)


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_default")
    search_fields = ("name",)
    list_filter = ("is_default",)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("user", "category", "amount", "date")
    search_fields = ("description", "user__email")
    list_filter = ("date", "category")


@admin.register(RecurringExpense)
class RecurringExpenseAdmin(admin.ModelAdmin):
    list_display = ("parent_expense", "date", "amount", "is_paid")
    list_filter = ("is_paid",)


@admin.register(AnomalyDetection)
class AnomalyDetectionAdmin(admin.ModelAdmin):
    list_display = ("user", "expense", "anomaly_type", "confidence_score")
    search_fields = ("user__email", "expense__description")
    list_filter = ("anomaly_type",)
