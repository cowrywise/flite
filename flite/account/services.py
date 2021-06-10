from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import transaction as db_transaction

from .models import (Account, Bank, BankTransfer, CardTransfer,
                     P2PTransfer)
from .serializers import (AccountSerializer, BankTransferSerializer,
                          CardTransferSerializer, P2PTransferSerializer)
from .utils import is_valid_uuid, randomStringDigits
from .models import User


class AccountService:
    """An Account service class containing account related methods."""

    @staticmethod
    def get_user_account(user: User) -> Account:
        """Get and return user account from user instance

        This method gets and locks the user account until
        commit is made. This is to prevent racing condition
        during account operations. It should only be called
        from a 'django transaction manager'.

        Args:
            user: User instance to get account.

        Returns:
            account: Account of user.
        """
        account = Account.objects.select_for_update().filter(
            owner=user).first()
        return account

    @staticmethod
    def get_user_account_from_id(id: str) -> Account:
        """Get and return user account from user id

        This method gets and locks the user account until
        commit is made. This is to prevent racing condition
        during account operations. It should only be called
        from a 'django transaction manager'.

        Args:
            id: User id to get account.

        Returns:
            account: Account of user.

        Exceptions:
            ObjectDoesNotExist: This error is raised if receipient of
            transaction is not found.
        """
        account = Account.objects.select_for_update().filter(id=id).first()
        if not account:
            raise ObjectDoesNotExist('No receipient found with this id')

        return account

    @classmethod
    def get_user_serialized_account(cls, user: User) -> dict:
        """Get and return serialized user account from user instance

        Args:
            user: User instance to get account.

        Returns:
            Seriailized account details
        """
        account = Account.objects.filter(owner=user).first()
        return AccountSerializer(account).data

    @staticmethod
    def create_type_based_transaction(card_or_bank: str, user: User, amount: float) -> None:
        """Get transaction type and create corresponding Transaction.

        Args:
            user: User instance that triggered the transaction.
            card_or_bank: String containing Transaction Type
            amount: Transaction amount
        """

        if isinstance(card_or_bank, Bank):
            BankTransfer.objects.create(owner=user,
                                        trans_type='Deposit',
                                        category='Credit',
                                        amount=amount,
                                        reference=randomStringDigits(),
                                        bank=card_or_bank)
        else:
            CardTransfer.objects.create(owner=user,
                                        trans_type='Deposit',
                                        category='Credit',
                                        amount=amount,
                                        reference=randomStringDigits(),
                                        card=card_or_bank)

    @classmethod
    def create_deposit_transaction(cls, data: dict, user: User) -> dict:
        """Create deposit transaction

        Args:
            data: Serialized transaction data
            user: User instance that triggered the transaction.

        Returns:
            Created serialized transaction object
        """
        amount, card_or_bank = data.values()
        with db_transaction.atomic():
            account = cls.get_user_account(user)
            account.available_balance += amount
            account.book_balance += amount
            cls.create_type_based_transaction(card_or_bank, user, amount)
            account.save()
            account.refresh_from_db()
        return AccountSerializer(account).data

    @classmethod
    def create_withdraw_transaction(cls, data: dict, user: User) -> dict:
        """Create withdraw transaction

        Args:
            data: Serialized transaction data
            user: User instance that triggered the transaction.

        Returns:
            Created serialized transaction object

        Exceptions:
            ValidationError: This error is raised if requested
            transaction amount is more than user balance.
        """
        amount, card_or_bank = data.values()
        with db_transaction.atomic():
            account = cls.get_user_account(user)
            if account.available_balance < amount:
                raise ValidationError('Transaction failed. Insufficient funds')

            account.available_balance -= amount
            account.book_balance -= amount
            BankTransfer.objects.create(owner=user,
                                        trans_type='Withraw',
                                        category='Debit',
                                        amount=amount,
                                        reference=randomStringDigits(),
                                        bank=card_or_bank)
            account.save()
            account.refresh_from_db()
            return AccountSerializer(account).data

    @classmethod
    def transfer(cls, user: User, receipient: str, amount: float) -> dict:
        """Create peer-to-peer transaction

        Args:
            id: User id to get account.

        Returns:
            account: Account of user.

        Exceptions:
            ValidationError: This error is raised if requested
            transaction amount is more than user balance.
        """
        with db_transaction.atomic():
            account = cls.get_user_account(user)
            receipient_acc = cls.get_user_account_from_id(receipient)
            if account.available_balance < amount:
                raise ValidationError('Transaction failed. Insufficient funds')

            account.available_balance -= amount
            account.book_balance -= amount
            receipient_acc.available_balance += amount
            receipient_acc.book_balance += amount
            P2PTransfer.objects.create(owner=user,
                                       trans_type='Transfer',
                                       category='Debit',
                                       amount=amount,
                                       reference=randomStringDigits(),
                                       receipient=receipient_acc)

            account.save()
            receipient_acc.save()
            account.refresh_from_db()

            return AccountSerializer(account).data

    @classmethod
    def get_transaction(cls, transaction_id: str, account_id: str) -> dict:
        """Get and Return transaction details.

        Args:
            transaction_id: Transaction id to get.
            account_id: account id to get.

        Returns:
            Serialized transaction object.

        Exceptions:
            ValidationError: This error is raised if requested
                transaction amount is more than user balance.
            ObjectDoesNotExist: This error is raised if no transaction
                with that id was found
        """

        if not is_valid_uuid(transaction_id):
            raise ValidationError('Please enter a valid transaction ID')

        if BankTransfer.objects.filter(id=transaction_id).exists():
            transaction = BankTransfer.objects.get(id=transaction_id)
            return BankTransferSerializer(transaction.banktransfer)
        elif CardTransfer.objects.filter(id=transaction_id).exists():
            transaction = CardTransfer.objects.get(id=transaction_id)
            return CardTransferSerializer(transaction.cardtransfer)
        elif P2PTransfer.objects.filter(id=transaction_id).exists():
            transaction = P2PTransfer.objects.get(id=transaction_id)
            if str(transaction.receipient.id) == account_id:
                transaction.p2ptransfer.category = 'Credit'
            return P2PTransferSerializer(transaction.p2ptransfer)
        raise ObjectDoesNotExist('No transaction found')
