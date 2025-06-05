from django.contrib import admin

from .models import (
    CreditFactor,
    CreditHistory,
    CreditFactorScore,
    CreditEstimation,
    ImprovementSuggestion,
)


@admin.register(CreditFactor)
class CreditFactorAdmin(admin.ModelAdmin):
    list_display = ("name", "weight")
    search_fields = ("name",)


@admin.register(CreditHistory)
class CreditHistoryAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "score")
    search_fields = ("user__email",)
    list_filter = ("date",)


@admin.register(CreditFactorScore)
class CreditFactorScoreAdmin(admin.ModelAdmin):
    list_display = ("credit_history", "factor", "score")
    list_filter = ("factor",)


@admin.register(CreditEstimation)
class CreditEstimationAdmin(admin.ModelAdmin):
    list_display = ("user", "estimated_score", "confidence_level", "created_at")
    search_fields = ("user__email",)
    list_filter = ("created_at",)


@admin.register(ImprovementSuggestion)
class ImprovementSuggestionAdmin(admin.ModelAdmin):
    list_display = ("credit_estimation", "title", "impact")
    list_filter = ("impact",)
    search_fields = ("title",)
