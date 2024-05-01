from celery import shared_task
from django.core.mail import send_mail
from django.db.models import Sum
from decimal import Decimal

@shared_task
def send_threshold_email(user_email, category_name, total_spending, subject):
    send_mail(
        subject,
        f'Your spending for {category_name} has reached {total_spending}.',
        'from@example.com',
        [user_email],
        fail_silently=False,
    )

def check_budget_threshold(instance):
    from .models import Transaction

    category = instance.category
    total_spending = Transaction.objects.filter(category=category).aggregate(Sum('amount'))['amount__sum']

    if total_spending is None:
        return

    budget = Decimal(str(category.max_spend))  # Convert budget to Decimal
    user_email = instance.owner.email

    if total_spending >= budget * Decimal('0.5') and total_spending < budget:
        send_threshold_email.delay(user_email, category.name, str(total_spending), 'Budget threshold warning')
    elif total_spending >= budget:
        send_threshold_email.delay(user_email, category.name, str(total_spending), 'Budget limit exceeded')

def check_budget_threshold_signal(sender, instance, **kwargs):
    check_budget_threshold(instance)