
from django.core.exceptions import ValidationError
from django.db import transaction as db_transaction

from .models import Bank, Card, BankTransfer, \
    CardTransfer, Account
from .utils import randomStringDigits
from .serializers import AccountSerializer


class AccountService:

    @classmethod
    def get_user_account(cls, user):
        account = Account.objects.select_for_update().filter(owner=user).first()
        return account

    @classmethod
    def create_type_based_transaction(cls, card_or_bank, user, amount):
        if isinstance(card_or_bank, Bank):
            BankTransfer.objects.create(
                owner=user,
                trans_type='Deposit',
                category='Credit',
                amount=amount,
                reference=randomStringDigits(),
                bank=card_or_bank
            )
        else:
            CardTransfer.objects.create(
                owner=user,
                trans_type='Deposit',
                category='Credit',
                amount=amount,
                reference=randomStringDigits(),
                card=card_or_bank
            )
    

    @classmethod
    def create_deposit_transaction(cls, data, user):
        amount, card_or_bank = data.values()
        with db_transaction.atomic():
            account = cls.get_user_account(user)
            account.available_balance += amount
            account.book_balance += amount
            cls.create_type_based_transaction(
                card_or_bank, user, amount
            )
            account.save()
            account.refresh_from_db()
        return AccountSerializer(account).data

    @classmethod
    def create_withdraw_transaction(cls, data, user):
        amount, card_or_bank = data.values()
        with db_transaction.atomic():
            account = cls.get_user_account(user)
            if account.available_balance < amount:
                raise ValidationError('Transaction failed. Insufficient funds')
                    
            account.available_balance -= amount
            account.book_balance -= amount
            BankTransfer.objects.create(
                owner=user,
                trans_type='Withraw',
                category='Debit',
                amount=amount,
                reference=randomStringDigits(),
                bank=card_or_bank
            )
            account.save()
            account.refresh_from_db()
            return AccountSerializer(account).data

