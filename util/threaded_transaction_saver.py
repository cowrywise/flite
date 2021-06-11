from decimal import Decimal

from flite.users.models import Transaction, Balance
from django.db.models import F


def t_transaction_saver(**kwargs):
    try:
        print("background task saving initiated")
        print(float(kwargs.get('amount')))
        f_amount = float(kwargs.get('amount'))
        balance_object_response = Transaction.objects.filter(
            owner=kwargs.get('owner')).order_by("-id").last()
        print(kwargs.get('owner'))
        print(kwargs.get("type"))
        print(balance_object_response)
        if balance_object_response:
            if "credit" in kwargs.get("type"):
                # new_balance_value = float(balance_object_response.new_balance)+f_amount
                print("crediting transaction list")
                # Transaction.objects.filter(
                #     owner=kwargs.get('owner'), reference=kwargs.get('reference')).update(
                #     new_balance=F("new_balance") + f_amount)
                new_balance_value = balance_object_response.new_balance + f_amount
                print(new_balance_value)
            elif "debit" in kwargs.get("type"):
                print("debiting transaction list")
                # Transaction.objects.filter(
                #     owner=kwargs.get('owner'), reference=kwargs.get('reference')).update(
                #     new_balance=F("new_balance") - f_amount)
                new_balance_value = balance_object_response.new_balance - f_amount
            transaction_saved = Transaction.objects.create(
                owner=kwargs.get('owner'),
                reference=kwargs.get('reference'),
                status=kwargs.get('status'),
                amount=f_amount,
                new_balance=new_balance_value
            )
        else:
            transaction_saved = Transaction.objects.create(
                owner=kwargs.get('owner'),
                reference=kwargs.get('reference'),
                status=kwargs.get('status'),
                amount=f_amount,
                new_balance=f_amount
            )

        if transaction_saved:
            print('t_transaction_saver saving done...')
        else:
            print('t_transaction_saver saving failed...')

    except Exception as e:
        print("Error at t_transaction_saver: ", str(e))
