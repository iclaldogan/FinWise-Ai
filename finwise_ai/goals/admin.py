from django.contrib import admin

from .models import SavingsGoal, GoalContribution, GoalMilestone


@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "target_amount", "current_amount", "status")
    search_fields = ("name", "user__email")
    list_filter = ("status", "priority")


@admin.register(GoalContribution)
class GoalContributionAdmin(admin.ModelAdmin):
    list_display = ("goal", "amount", "date")
    list_filter = ("date",)


@admin.register(GoalMilestone)
class GoalMilestoneAdmin(admin.ModelAdmin):
    list_display = ("goal", "name", "target_amount", "target_date", "is_reached")
    list_filter = ("is_reached",)
