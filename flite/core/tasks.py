from celery import shared_task
from django.core.mail import send_mail
from django.db.models import Sum
from flite.core.models import Transaction  # Import models
from decimal import Decimal

@shared_task
def check_budget_threshold(transaction_id):
    transaction = Transaction.objects.get(id=transaction_id)
    category = transaction.category
    total_spending = Transaction.objects.filter(category=category).aggregate(Sum('amount'))['amount__sum']
    budget = category.max_spend

    if total_spending is None:
        return

    if total_spending >= budget * Decimal('0.5'):
        user_email = transaction.owner.email
        send_mail(
            'Budget threshold warning',
            f'Your spending for {category.name} has reached {total_spending}, which is over 50% of your budget.',
            'from@example.com',
            [user_email],
            fail_silently=False,
        )