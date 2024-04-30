from celery import shared_task
from django.core.mail import send_mail
from .models import BudgetCategory, Transaction

@shared_task
def check_budget_threshold():
    for category in BudgetCategory.objects.all():
        total_spend = Transaction.objects.filter(category=category).aggregate(Sum('amount'))['amount__sum']
        if total_spend >= category.max_spend * 0.5:
            send_mail(
                'Budget threshold warning',
                f'Your spending for {category.name} has reached {total_spend}, which is over 50% of your budget.',
                'from@example.com',
                [category.owner.email],
                fail_silently=False,
            )