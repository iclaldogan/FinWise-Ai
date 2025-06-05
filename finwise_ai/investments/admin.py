from django.contrib import admin

from .models import (
    InvestmentType,
    Investment,
    InvestmentTransaction,
    InvestmentSimulation,
    SimulationResult,
)


@admin.register(InvestmentType)
class InvestmentTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "risk_level")
    search_fields = ("name",)
    list_filter = ("category",)


@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "investment_type",
        "name",
        "quantity",
        "status",
    )
    search_fields = ("name", "user__email")
    list_filter = ("status",)


@admin.register(InvestmentTransaction)
class InvestmentTransactionAdmin(admin.ModelAdmin):
    list_display = ("investment", "transaction_type", "date", "quantity")
    list_filter = ("transaction_type", "date")


@admin.register(InvestmentSimulation)
class InvestmentSimulationAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "strategy", "created_at")
    search_fields = ("name", "user__email")
    list_filter = ("strategy", "created_at")


@admin.register(SimulationResult)
class SimulationResultAdmin(admin.ModelAdmin):
    list_display = ("simulation", "year", "month", "investment_value")
    list_filter = ("year", "month")
