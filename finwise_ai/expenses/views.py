from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Expense, ExpenseCategory, RecurringExpense, AnomalyDetection
from .forms import ExpenseForm, ExpenseCategoryForm, ExpenseFilterForm, RecurringExpenseForm
import json
import pandas as pd
import numpy as np

@login_required
def expense_home(request):
    """View for the expenses dashboard."""
    # Get filter parameters
    form = ExpenseFilterForm(request.GET, user=request.user)
    
    # Base queryset
    expenses = Expense.objects.filter(user=request.user)
    
    # Apply filters if form is valid
    if form.is_valid():
        if form.cleaned_data.get('start_date'):
            expenses = expenses.filter(date__gte=form.cleaned_data['start_date'])
        if form.cleaned_data.get('end_date'):
            expenses = expenses.filter(date__lte=form.cleaned_data['end_date'])
        if form.cleaned_data.get('category'):
            expenses = expenses.filter(category=form.cleaned_data['category'])
        if form.cleaned_data.get('min_amount'):
            expenses = expenses.filter(amount__gte=form.cleaned_data['min_amount'])
        if form.cleaned_data.get('max_amount'):
            expenses = expenses.filter(amount__lte=form.cleaned_data['max_amount'])
        if form.cleaned_data.get('description'):
            expenses = expenses.filter(description__icontains=form.cleaned_data['description'])
    
    # Get expense categories for the pie chart
    categories = ExpenseCategory.objects.all()
    category_data = []
    
    for category in categories:
        category_sum = expenses.filter(category=category).aggregate(Sum('amount'))['amount__sum'] or 0
        if category_sum > 0:
            category_data.append({
                'name': category.name,
                'amount': float(category_sum),
                'color': category.color or '#1DE9B6'
            })
    
    # Get monthly totals for the line chart
    today = timezone.now().date()
    six_months_ago = today - timedelta(days=180)
    
    monthly_expenses = (
        expenses
        .filter(date__gte=six_months_ago)
        .values('date__year', 'date__month')
        .annotate(total=Sum('amount'))
        .order_by('date__year', 'date__month')
    )
    
    monthly_data = []
    for entry in monthly_expenses:
        month_name = datetime(entry['date__year'], entry['date__month'], 1).strftime('%b %Y')
        monthly_data.append({
            'month': month_name,
            'amount': float(entry['total'])
        })
    
    # Get flagged expenses (anomalies)
    flagged_expenses = expenses.filter(is_flagged=True).order_by('-date')[:5]
    
    # Get recurring expenses
    recurring_expenses = expenses.filter(recurrence__in=['daily', 'weekly', 'monthly', 'yearly']).order_by('-date')[:5]
    
    context = {
        'expenses': expenses.order_by('-date')[:10],
        'filter_form': form,
        'category_data': json.dumps(category_data),
        'monthly_data': json.dumps(monthly_data),
        'flagged_expenses': flagged_expenses,
        'recurring_expenses': recurring_expenses,
        'total_expenses': expenses.aggregate(Sum('amount'))['amount__sum'] or 0,
        'avg_monthly': expenses.filter(date__gte=six_months_ago).aggregate(Avg('amount'))['amount__avg'] or 0,
    }
    
    return render(request, 'expenses/expense_home.html', context)

@login_required
def expense_list(request):
    """View for listing all expenses."""
    # Get filter parameters
    form = ExpenseFilterForm(request.GET, user=request.user)
    
    # Base queryset
    expenses = Expense.objects.filter(user=request.user)
    
    # Apply filters if form is valid
    if form.is_valid():
        if form.cleaned_data.get('start_date'):
            expenses = expenses.filter(date__gte=form.cleaned_data['start_date'])
        if form.cleaned_data.get('end_date'):
            expenses = expenses.filter(date__lte=form.cleaned_data['end_date'])
        if form.cleaned_data.get('category'):
            expenses = expenses.filter(category=form.cleaned_data['category'])
        if form.cleaned_data.get('min_amount'):
            expenses = expenses.filter(amount__gte=form.cleaned_data['min_amount'])
        if form.cleaned_data.get('max_amount'):
            expenses = expenses.filter(amount__lte=form.cleaned_data['max_amount'])
        if form.cleaned_data.get('description'):
            expenses = expenses.filter(description__icontains=form.cleaned_data['description'])
    
    context = {
        'expenses': expenses.order_by('-date'),
        'filter_form': form,
    }
    
    return render(request, 'expenses/expense_list.html', context)

@login_required
def expense_create(request):
    """View for creating a new expense."""
    if request.method == 'POST':
        form = ExpenseForm(request.POST, user=request.user)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            
            # Handle recurring expenses
            if expense.recurrence != 'none' and expense.recurrence_end_date:
                create_recurring_expenses(expense)
            
            # Check for anomalies
            detect_anomalies(expense)
            
            messages.success(request, 'Expense created successfully!')
            return redirect('expense_list')
    else:
        form = ExpenseForm(user=request.user)
    
    context = {
        'form': form,
        'title': 'Add Expense',
    }
    
    return render(request, 'expenses/expense_form.html', context)

@login_required
def expense_edit(request, pk):
    """View for editing an existing expense."""
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense, user=request.user)
        if form.is_valid():
            expense = form.save()
            
            # Update recurring expenses if needed
            if expense.recurrence != 'none':
                update_recurring_expenses(expense)
            
            messages.success(request, 'Expense updated successfully!')
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense, user=request.user)
    
    context = {
        'form': form,
        'expense': expense,
        'title': 'Edit Expense',
    }
    
    return render(request, 'expenses/expense_form.html', context)

@login_required
def expense_delete(request, pk):
    """View for deleting an expense."""
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    
    if request.method == 'POST':
        # Delete recurring instances if this is a recurring expense
        if expense.recurrence != 'none':
            RecurringExpense.objects.filter(parent_expense=expense).delete()
        
        expense.delete()
        messages.success(request, 'Expense deleted successfully!')
        return redirect('expense_list')
    
    context = {
        'expense': expense,
    }
    
    return render(request, 'expenses/expense_confirm_delete.html', context)

@login_required
def category_list(request):
    """View for listing expense categories."""
    categories = ExpenseCategory.objects.all()
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'expenses/category_list.html', context)

@login_required
def category_create(request):
    """View for creating a new expense category."""
    if request.method == 'POST':
        form = ExpenseCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('category_list')
    else:
        form = ExpenseCategoryForm()
    
    context = {
        'form': form,
        'title': 'Add Category',
    }
    
    return render(request, 'expenses/category_form.html', context)

@login_required
def category_edit(request, pk):
    """View for editing an existing expense category."""
    category = get_object_or_404(ExpenseCategory, pk=pk)
    
    if request.method == 'POST':
        form = ExpenseCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('category_list')
    else:
        form = ExpenseCategoryForm(instance=category)
    
    context = {
        'form': form,
        'category': category,
        'title': 'Edit Category',
    }
    
    return render(request, 'expenses/category_form.html', context)

@login_required
def recurring_expenses(request):
    """View for managing recurring expenses."""
    recurring = RecurringExpense.objects.filter(
        parent_expense__user=request.user,
        date__gte=timezone.now().date()
    ).order_by('date')
    
    context = {
        'recurring_expenses': recurring,
    }
    
    return render(request, 'expenses/recurring_expenses.html', context)

@login_required
def recurring_expense_edit(request, pk):
    """View for editing a recurring expense instance."""
    recurring = get_object_or_404(RecurringExpense, pk=pk, parent_expense__user=request.user)
    
    if request.method == 'POST':
        form = RecurringExpenseForm(request.POST, instance=recurring)
        if form.is_valid():
            recurring = form.save(commit=False)
            recurring.is_modified = True
            recurring.save()
            messages.success(request, 'Recurring expense updated successfully!')
            return redirect('recurring_expenses')
    else:
        form = RecurringExpenseForm(instance=recurring)
    
    context = {
        'form': form,
        'recurring': recurring,
    }
    
    return render(request, 'expenses/recurring_expense_form.html', context)

@login_required
def anomaly_detection(request):
    """View for displaying expense anomalies."""
    anomalies = AnomalyDetection.objects.filter(
        user=request.user,
        is_reviewed=False
    ).order_by('-created_at')
    
    context = {
        'anomalies': anomalies,
    }
    
    return render(request, 'expenses/anomaly_detection.html', context)

@login_required
def mark_anomaly_reviewed(request, pk):
    """View for marking an anomaly as reviewed."""
    anomaly = get_object_or_404(AnomalyDetection, pk=pk, user=request.user)
    
    if request.method == 'POST':
        is_false_positive = request.POST.get('is_false_positive') == 'true'
        anomaly.is_reviewed = True
        anomaly.is_false_positive = is_false_positive
        anomaly.save()
        
        # If it's not a false positive, keep the expense flagged
        if not is_false_positive:
            anomaly.expense.is_flagged = True
            anomaly.expense.save()
        else:
            anomaly.expense.is_flagged = False
            anomaly.expense.save()
        
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def expense_analytics(request):
    """View for advanced expense analytics."""
    # Get all expenses for the user
    expenses = Expense.objects.filter(user=request.user)
    
    # Convert to pandas DataFrame for analysis
    expense_data = list(expenses.values('date', 'amount', 'category__name', 'description'))
    df = pd.DataFrame(expense_data)
    
    if not df.empty:
        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Monthly trend
        monthly_trend = df.groupby(df['date'].dt.strftime('%Y-%m')).agg({
            'amount': 'sum'
        }).reset_index()
        monthly_trend = monthly_trend.sort_values('date')
        
        # Category breakdown
        category_breakdown = df.groupby('category__name').agg({
            'amount': 'sum'
        }).reset_index()
        category_breakdown = category_breakdown.sort_values('amount', ascending=False)
        
        # Day of week analysis
        df['day_of_week'] = df['date'].dt.day_name()
        day_of_week = df.groupby('day_of_week').agg({
            'amount': 'sum'
        }).reset_index()
        
        # Largest expenses
        largest_expenses = df.sort_values('amount', ascending=False).head(10)
        
        context = {
            'monthly_trend': monthly_trend.to_dict('records'),
            'category_breakdown': category_breakdown.to_dict('records'),
            'day_of_week': day_of_week.to_dict('records'),
            'largest_expenses': largest_expenses.to_dict('records'),
            'total_expenses': df['amount'].sum(),
            'avg_monthly': df.groupby(df['date'].dt.strftime('%Y-%m'))['amount'].sum().mean(),
            'num_transactions': len(df),
        }
    else:
        context = {
            'no_data': True
        }
    
    return render(request, 'expenses/expense_analytics.html', context)

# Helper functions

def create_recurring_expenses(expense):
    """Create recurring expense instances based on the recurrence pattern."""
    from dateutil.relativedelta import relativedelta
    
    start_date = expense.date
    end_date = expense.recurrence_end_date
    
    current_date = start_date
    
    while current_date <= end_date:
        if current_date > start_date:  # Skip the first one (it's the original expense)
            RecurringExpense.objects.create(
                parent_expense=expense,
                amount=expense.amount,
                date=current_date,
                is_paid=False
            )
        
        # Calculate next date based on recurrence pattern
        if expense.recurrence == 'daily':
            current_date += timedelta(days=1)
        elif expense.recurrence == 'weekly':
            current_date += timedelta(weeks=1)
        elif expense.recurrence == 'monthly':
            current_date += relativedelta(months=1)
        elif expense.recurrence == 'yearly':
            current_date += relativedelta(years=1)

def update_recurring_expenses(expense):
    """Update recurring expense instances after the parent expense is modified."""
    # Delete future recurring instances that haven't been modified
    RecurringExpense.objects.filter(
        parent_expense=expense,
        date__gt=timezone.now().date(),
        is_modified=False
    ).delete()
    
    # Create new recurring instances
    if expense.recurrence != 'none' and expense.recurrence_end_date:
        create_recurring_expenses(expense)

def detect_anomalies(expense):
    """Detect anomalies in expenses using simple statistical methods."""
    # Get user's expenses in the same category from the last 6 months
    six_months_ago = timezone.now().date() - timedelta(days=180)
    category_expenses = Expense.objects.filter(
        user=expense.user,
        category=expense.category,
        date__gte=six_months_ago,
        date__lt=expense.date  # Exclude the current expense
    )
    
    if category_expenses.count() >= 5:  # Need enough data for meaningful analysis
        # Calculate mean and standard deviation
        amounts = [e.amount for e in category_expenses]
        mean = np.mean(amounts)
        std_dev = np.std(amounts)
        
        # Check if current expense is an outlier (> 2 standard deviations from mean)
        if expense.amount > mean + (2 * std_dev):
            # Create anomaly detection record
            AnomalyDetection.objects.create(
                user=expense.user,
                expense=expense,
                anomaly_type='spike',
                confidence_score=min(1.0, (expense.amount - mean) / (3 * std_dev)),
                description=f"This expense is significantly higher than your usual spending in this category. Average: {mean:.2f}, This expense: {expense.amount:.2f}"
            )
            
            # Flag the expense
            expense.is_flagged = True
            expense.save()
