import json
from django.db import transaction
from django.db.models import F
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.status import HTTP_201_CREATED, HTTP_403_FORBIDDEN
from .permissions import IsUserOrReadOnly
from . import constants
from .utils import generate_transaction_referencecode
from .models import (
    User, 
    UserProfile, 
    Account, 
    Transaction
)
from .serializers import (
    CreateUserSerializer, 
    UserSerializer, 
    WithdrawalDepositSerializer,
    TransferSerializer, 
    TransactionSerializer, 
    AccountSerializer
)

class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """
    Updates and retrieves user accounts
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsUserOrReadOnly,)

    @transaction.atomic
    @action(detail=True, methods=['post'])
    def deposits(self, request, pk=None):
        user = self.get_object()
        serializer = WithdrawalDepositSerializer(data=request.data)
        if serializer.is_valid() and user:
            account_number = serializer.validated_data.get('account_number')
            amount = serializer.validated_data.get('amount')
            account = Account.objects.get(owner=user, account_number=account_number)
            account.account_balance = F('account_balance') + amount
            account.save()
            account.refresh_from_db()

            # create transaction for deposit action
            Transaction.objects.create(
                owner=account,
                transaction_type=constants.CREDIT,
                transaction_action=constants.DEPOSIT,
                transaction_journal=json.dumps({
                    "account": account_number,
                    "amount_credited": float(amount),
                    "current_balance": float(account.account_balance)
                }),
                reference=generate_transaction_referencecode()
            )
            return Response(data={"message": "Account deposit successfull"})
        return Response(data={"message": serializer.error_messages})


    @transaction.atomic
    @action(detail=True, methods=['post', 'get'])
    def withdrawals(self, request, pk=None):
        user = self.get_object()
        serializer = WithdrawalDepositSerializer(data=request.data)
        if serializer.is_valid() and user:
            account_number = serializer.validated_data.get('account_number')
            amount = serializer.validated_data.get('amount')
            account = Account.objects.get(owner=user, account_number=account_number)
            if account.account_balance < amount or account.account_balance == 0:
                return Response(data={"message": "Account balance too low to withdraw"}, status=HTTP_403_FORBIDDEN)
            account.account_balance = F('account_balance') - amount
            account.save()
            account.refresh_from_db()
            # create transaction for withrawal action
            Transaction.objects.create(
                owner=account,
                transaction_type=constants.DEBIT,
                transaction_action=constants.WITHDRAWAL,
                transaction_journal=json.dumps({
                    "account": account_number,
                    "amount_debited": float(amount),
                    "current_balance": float(account.account_balance)
                }),
                reference=generate_transaction_referencecode()
            )

            return Response(data={"message": "Account withdrawal successfull"})
        return Response(data={"message": serializer.error_messages})


    def get_serializer_class(self):
        if self.action in ('deposits', 'withdrawals'):
            return WithdrawalDepositSerializer
        return super().get_serializer_class()


class UserCreateViewSet(mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    """
    Creates user accounts
    """
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = (AllowAny,)


class AccountViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Get account information
    """
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    @transaction.atomic
    @action(detail=True, methods=['post'], url_path="transfers/(?P<recipient_account_pk>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})", url_name="account-transfers")
    def transfers(self, request, pk=None, recipient_account_pk=None):
        sender_account = self.get_object()
        serializer = TransferSerializer(data=request.data)
        serializer.is_valid()
        if sender_account:
            try:
                recipient_account = Account.objects.get(id=recipient_account_pk)
                if sender_account.id == recipient_account.id:
                    raise Exception("Can't transfer funds to same account as accounts with ID '%s' and '%s'" % (sender_account.id, recipient_account.id))
            except Account.DoesNotExist as error:
                return Response(data={"message": str(error)})
            except Exception as error:
                return Response(data={"message": str(error)})
            else:
                amount = serializer.validated_data.get('amount')
                if sender_account.account_balance < amount or sender_account.account_balance == 0:
                    return Response(data={"message": "Account balance too low to withdraw"}, status=HTTP_403_FORBIDDEN)
                sender_account.account_balance = F('account_balance') - amount
                recipient_account.account_balance = F('account_balance') + amount
                sender_account.save()
                recipient_account.save()
                # refresh DB values
                sender_account.refresh_from_db()
                recipient_account.refresh_from_db()

                transaction_ref_id = generate_transaction_referencecode()
                
                # create transaction for transfer action
                Transaction.objects.create(
                    owner=sender_account,
                    transaction_type=constants.DEBIT,
                    transaction_action=constants.TRANSFER,
                    transaction_journal=json.dumps({
                        "sender_account": sender_account.account_number,
                        "recipient_account": recipient_account.account_number,
                        "amount_debited": float(amount),
                        "sender_current_balance": float(sender_account.account_balance)
                    }),
                    reference=transaction_ref_id
                )

                Transaction.objects.create(
                    owner=recipient_account,
                    transaction_type=constants.CREDIT,
                    transaction_action=constants.TRANSFER,
                    transaction_journal=json.dumps({
                        "sender_account": sender_account.account_number,
                        "recipient_account": recipient_account.account_number,
                        "amount_credited": float(amount),
                        "recipient_current_balance": float(recipient_account.account_balance)
                    }),
                    reference=transaction_ref_id
                )

                return Response(data={"message": "Amount => %s" % amount})
        return Response(data={"message": "Sender account does not exist, please ensure you specify already existing account id"})


    def get_serializer_class(self):
        if self.action == 'transfers':
            return TransferSerializer
        return super().get_serializer_class()
class TransactionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Get transactions performed on an account
    """
    serializer_class = TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(owner=self.kwargs['transactions_pk'])