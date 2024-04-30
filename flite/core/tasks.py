from celery import shared_task
from django.core.mail import send_mail
from django.db.models import Sum
from flite.core.models import BudgetCategory, Transaction


@shared_task
def check_budget_threshold():
    print("Running check_budget_threshold task")
    print("Sending budget threshold warning email")
    send_mail(
            'Budget threshold warning',
            f'Your spending for {category.name} has reached {total_spend}, which is over 50% of your budget.',
            'from@example.com',
            [category.owner.email],
            fail_silently=False,
        )