from django.db import transaction, DatabaseError
from django.db.models import Sum
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import User, NewUserPhoneVerification, Transaction, P2PTransfer
from .permissions import IsUserOrReadOnly, IsTransactionOwner
from .serializers import CreateUserSerializer, UserSerializer, SendNewPhonenumberSerializer, AmountSerializer, \
    TransactionSerializer
from . import utils


class TransactionViewSet(viewsets.GenericViewSet):
    """
    deposit and withdraws
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = (AllowAny,)
    lookup_url_kwarg = 'account_id'
    lookup_field = 'owner'

    @action(detail=True, methods=['get'], url_path='transactions', permission_classes=[IsTransactionOwner])
    def fetch_all_transactions(self, request, account_id):
        transactions = get_list_or_404(self.get_queryset(), owner__id=account_id)

        pages = self.paginate_queryset(transactions)
        if pages is not None:
            data = self.serializer_class(pages, many=True).data
            return self.get_paginated_response(data)

        data = self.serializer_class(transactions, many=True).data
        return Response(data)

    @action(detail=True, methods=['get'], permission_classes=[IsTransactionOwner],
            url_path='transactions/(?P<transaction_id>[^/.]+)')
    def fetch_a_single_transaction(self, request, account_id, transaction_id):
        transaction_obj = get_object_or_404(self.get_queryset(), owner__id=account_id, id=transaction_id)
        transaction_serializer = self.serializer_class(transaction_obj)
        return Response(transaction_serializer.data)


class UserTransactionViewSet(viewsets.GenericViewSet):
    """
    deposit and withdraws
    """
    queryset = Transaction.objects.all()
    serializer_class = AmountSerializer
    permission_classes = (AllowAny,)
    lookup_url_kwarg = 'user_id'
    lookup_field = 'owner__id'

    @action(detail=True, methods=['post'])
    def deposits(self, request, user_id):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount = serializer.data.get("amount")
        Transaction.objects.create(
            owner=User.objects.get(id=user_id), reference='deposit', amount=amount, status='deposited'
        )

        content = {
            'status': True,
            'message': "Amount Deposited successfully",
        }
        return Response(content, 200)

    @action(detail=True, methods=['post'], permission_classes=[IsTransactionOwner])
    def withdrawals(self, request, user_id):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.data.get("amount")

        balance = Transaction.objects.filter(owner__id=user_id).aggregate(balance=Sum('amount'))['balance']

        if balance is None or amount > balance:
            return Response({
                'status': False,
                'message': "You can't withdraw more than you have",
            }, 400
            )

        Transaction.objects.create(
            owner=User.objects.get(id=user_id), reference='withdrawal', amount=-amount, status='withdrawn'
        )

        return Response({
            'status': True,
            'message': "Amount Withdrawn successfully",
        }, 200
        )


class AccountTransactionViewSet(viewsets.GenericViewSet):
    """
    P2P Transfers, all transactions, retrieve transaction
    """
    serializer_class = AmountSerializer
    permission_classes = (AllowAny,)
    lookup_url_kwarg = 'sender_account_id'
    lookup_field = 'user__id'

    @action(detail=True, methods=['post'], permission_classes=[IsTransactionOwner],
            url_path='p2p_transfer/(?P<recipient_account_id>[^/.]+)')
    def p2p_transfer(self, request, sender_account_id, recipient_account_id):
        # validate amount
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.data.get("amount")

        # check sender balance to see if transfer can be made
        balance = Transaction.objects.filter(owner__id=sender_account_id).aggregate(balance=Sum('amount'))['balance']

        if balance is None or amount > balance:
            return Response({
                'status': False,
                'message': "You can't transfer more than you have",
            }, 400
            )

        sender = get_object_or_404(User, id=sender_account_id)
        recipient = get_object_or_404(User, id=recipient_account_id)

        # make transfer atomic
        try:
            with transaction.atomic():
                # debit sender
                Transaction.objects.create(
                    owner=sender, reference='p2p_sender', amount=-amount, status='withdrawn'
                )

                Transaction.objects.create(
                    owner=recipient, reference='p2p_recipient', amount=amount, status='deposited'
                )

                # credit receiver
                P2PTransfer.objects.create(
                    sender=sender, recipient=recipient,
                    owner=recipient, reference='p2p_transfer', amount=amount, status='p2p_transferred'
                )

        except DatabaseError as e:
            print(e)
            return Response({
                'status': False,
                'message': "There was an error trying to make Transfer!",
            }, 400
            )

        return Response({
            'status': True,
            'message': "Amount Deposited successfully",
        }, 200
        )


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """
    Updates and retrieves user accounts
    Also deposit and withdraws
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsUserOrReadOnly,)


class UserCreateViewSet(mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    """
    Creates user accounts
    """
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = (AllowAny,)


class SendNewPhonenumberVerifyViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    Sending of verification code
    """
    queryset = NewUserPhoneVerification.objects.all()
    serializer_class = SendNewPhonenumberSerializer
    permission_classes = (AllowAny,)

    def update(self, request, pk=None, **kwargs):
        verification_object = self.get_object()
        code = request.data.get("code")

        if code is None:
            return Response({"message": "Request not successful"}, 400)

        if verification_object.verification_code != code:
            return Response({"message": "Verification code is incorrect"}, 400)

        code_status, msg = utils.validate_mobile_signup_sms(verification_object.phone_number, code)

        content = {
            'verification_code_status': str(code_status),
            'message': msg,
        }
        return Response(content, 200)
