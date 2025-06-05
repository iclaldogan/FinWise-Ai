from django.contrib import admin

from .models import (
    LoanType,
    Loan,
    LoanPayment,
    LoanEligibility,
)


@admin.register(LoanType)
class LoanTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "min_amount", "max_amount", "base_interest_rate")
    search_fields = ("name",)


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ("user", "loan_type", "amount", "status", "created_at")
    search_fields = ("user__email",)
    list_filter = ("status", "created_at")


@admin.register(LoanPayment)
class LoanPaymentAdmin(admin.ModelAdmin):
    list_display = ("loan", "payment_date", "amount", "is_paid")
    list_filter = ("is_paid",)


@admin.register(LoanEligibility)
class LoanEligibilityAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "loan_type",
        "is_eligible",
        "offered_interest_rate",
        "created_at",
    )
    search_fields = ("user__email",)
    list_filter = ("is_eligible", "created_at")
