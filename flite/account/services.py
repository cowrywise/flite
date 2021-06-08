
from .models import Bank, Card, BankTransfer, \
    CardTransfer
from .utils import randomStringDigits


class AccountService:

    @staticmethod
    def create_deposit_transaction(data, user):
        amount, card_or_bank = data.values()
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

    @staticmethod
    def create_withdraw_transaction(data, user):
        amount, card_or_bank = data.values()
        BankTransfer.objects.create(
            owner=user,
            trans_type='Withraw',
            category='Debit',
            amount=amount,
            reference=randomStringDigits(),
            bank=card_or_bank
        )
