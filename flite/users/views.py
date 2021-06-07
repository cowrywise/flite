from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import detail_route
from rest_framework.generics import GenericAPIView
from rest_framework import pagination
from .models import User, NewUserPhoneVerification, Balance, Transaction, P2PTransfer
from .permissions import IsUserOrReadOnly, IsAccountOwner, IsWalletOwner
from .serializers import CreateUserSerializer, UserSerializer, SendNewPhonenumberSerializer, UserTransactionSerializer, TransactionSerializer, P2PTransactionSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from . import utils
from flite.users import serializers
from django import db
from decimal import Decimal
from decimal import getcontext

class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """
    Updates and retrieves user accounts
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsUserOrReadOnly,)

    def get_serializer_class(self):
        if self.action not in ['deposits', 'withdrawals']:
            return UserSerializer
        return UserTransactionSerializer

    def get_serializer_context(self):
        if self.action not in ['deposits', 'withdrawals']:
            return super().get_serializer_context()
        context = super().get_serializer_context()
        context['transaction_type'] = self.action
        return context
    @detail_route(methods=['POST'])
    def deposits(self, request, *args, **kwargs):
        # when a deposit is made update transactions and balance tables
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reference_id = utils.generate_reference_id()
        deposited_amount = serializer.validated_data['amount']
        available_balance = Balance.objects.filter(
            owner=request.user).order_by('-modified').first().available_balance
        new_available_balance = Decimal(
            available_balance) + Decimal(deposited_amount)

        try:
            with db.transaction.atomic():
                # create a new balance
                new_balance_details = {'owner': request.user,
                                       'available_balance': new_available_balance,
                                       'book_balance': new_available_balance}
                new_balance = Balance.objects.create(**new_balance_details)
                # record transaction
                transaction_details = {'owner': request.user,
                                       'reference': reference_id,
                                       'status': 'completed',
                                       'amount': deposited_amount,
                                       'new_balance': new_balance.available_balance}
                transaction = Transaction.objects.create(**transaction_details)
        except:
            return Response({"error": "unale to complete transaction"}, 400)
        content = {'transaction_id': transaction.id,
                   'amount': Decimal(deposited_amount),
                   'transaction_type': 'credit',
                   'available_balance': new_balance.available_balance,
                   'status': 'completed',
                   'reference': reference_id,
                   'created': transaction.created,
                   'updated': transaction.modified}
        return Response(content, 201)

    @detail_route(methods=['POST'])
    def withdrawals(self, request, *args, **kwargs):
        # when a deposit is made update transactions and balance tables
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reference_id = utils.generate_reference_id()
        withdrawn_amount = serializer.validated_data['amount']
        available_balance = Balance.objects.filter(
            owner=request.user).order_by('-modified').first().available_balance
        new_available_balance = Decimal(
            available_balance) - Decimal(withdrawn_amount)
        try:
            with db.transaction.atomic():
                # create a new balance
                new_balance_details = {'owner': request.user,
                                       'available_balance': new_available_balance,
                                       'book_balance': new_available_balance}
                new_balance = Balance.objects.create(**new_balance_details)
                # record transaction
                transaction_details = {'owner': request.user,
                                       'reference': reference_id,
                                       'status': 'completed',
                                       'amount': Decimal(-withdrawn_amount),
                                       'new_balance': new_balance.available_balance}
                transaction = Transaction.objects.create(**transaction_details)
        except:
            return Response({"error": "unale to complete transaction"}, 400)
        content = {'transaction_id': transaction.id,
                   'amount': Decimal(withdrawn_amount),
                   'transaction_type': 'debit',
                   'available_balance': new_balance.available_balance,
                   'status': 'completed',
                   'reference': reference_id,
                   'created': transaction.created,
                   'updated': transaction.modified}
        return Response(content, 201)


class UserCreateViewSet(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    """
    Creates user accounts
    """
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = (AllowAny,)


class SendNewPhonenumberVerifyViewSet(mixins.CreateModelMixin,mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    Sending of verification code
    """
    queryset = NewUserPhoneVerification.objects.all()
    serializer_class = SendNewPhonenumberSerializer
    permission_classes = (AllowAny,)


    def update(self, request, pk=None,**kwargs):
        verification_object = self.get_object()
        code = request.data.get("code")

        if code is None:
            return Response({"message":"Request not successful"}, 400)    

        if verification_object.verification_code != code:
            return Response({"message":"Verification code is incorrect"}, 400)    

        code_status, msg = utils.validate_mobile_signup_sms(verification_object.phone_number, code)
        
        content = {
                'verification_code_status': str(code_status),
                'message': msg,
        }
        return Response(content, 200)    

class AccountTransactionListView(GenericAPIView):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()
    lookup_url_kwarg = 'account_id'
    permission_classes = [IsAccountOwner]

    def get(self, request, *args, **kwargs):
        transactions = self.get_queryset().filter(owner=request.user)
        serializer = self.serializer_class(transactions, many=True)
        return Response(serializer.data, 200)


class AccountTransactionDetailView(GenericAPIView):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()
    lookup_url_kwarg = 'account_id'
    permission_classes = [IsAccountOwner]
    pagination_class = pagination.PageNumberPagination

    def get(self, request, *args, **kwargs):
        transaction = self.get_queryset().get(id=kwargs['transaction_id'])
        serializer = self.serializer_class(transaction)
        return Response(serializer.data, 200)

class P2PAPIView(GenericAPIView):
    serializer_class = P2PTransactionSerializer
    permission_classes = [IsWalletOwner]
    lookup_url_kwarg = 'sender_id'

    def post(self, request, *args, **kwargs):
        sender_id = kwargs['sender_account_id']
        recepient_id = kwargs['recipient_account_id']
        context = {'sender_id': sender_id, 'recepient_id': recepient_id}
        # pass sender and recipient_id in context_dict
        serializer = self.serializer_class(data=request.data, context=context)
        # validate serializer
        serializer.is_valid(raise_exception=True)
        reference_id = utils.generate_reference_id()
        try:
            with db.transaction.atomic():
                # debit the sender
                sender_balance = Balance.objects.filter(owner=request.user).order_by(
                    '-modified').first().available_balance
                amount_to_send = serializer.validated_data['amount']
                sender_new_balance = Decimal(
                    sender_balance) - Decimal(amount_to_send)
                sender_new_balance_details = {'owner': request.user,
                                              'available_balance': sender_new_balance,
                                              'book_balance': sender_new_balance}
                # update balance & record transaction
                sender_new_balance_record = Balance.objects.create(
                    **sender_new_balance_details)
                sender_transaction_details = {'owner': request.user,
                                              'reference': reference_id,
                                              'status': 'completed',
                                              'amount': -amount_to_send,
                                              'new_balance': sender_new_balance_record.available_balance}
                sender_transaction_record = Transaction.objects.create(
                    **sender_transaction_details)
                # credit the recipient
                recepient = User.objects.get(id=recepient_id)
                recepient_balance = Balance.objects.filter(
                    owner=recepient).order_by('-modified').first().available_balance
                recepient_new_balance = Decimal(
                    recepient_balance) + Decimal(amount_to_send)
                recepient_new_balance_details = {'owner': recepient,
                                                 'available_balance': recepient_new_balance,
                                                 'book_balance': recepient_new_balance}
                # update balance & record transaction
                recepient_new_balance_record = Balance.objects.create(
                    **recepient_new_balance_details)
                recepient_transaction_details = {'owner': recepient,
                                                 'reference': reference_id,
                                                 'status': 'completed',
                                                 'amount': amount_to_send,
                                                 'new_balance': recepient_new_balance_record.available_balance}
                recepient_transaction_record = Transaction.objects.create(
                    **recepient_transaction_details)
                # create p2p transactions with same ref_id
                p2p_transaction_details = {'owner': request.user,
                                           'reference': reference_id,
                                           'status': 'completed',
                                           'amount': amount_to_send,
                                           'new_balance': sender_new_balance_record.available_balance,
                                           'sender': request.user,
                                           'receipient': recepient}
                p2p_transaction_record = P2PTransfer.objects.create(
                    **p2p_transaction_details)
        except:
            return Response({"error": "unale to complete transaction"}, 400)
        # send response back to the view
        serializer = self.serializer_class(p2p_transaction_record)
        return Response(serializer.data, 201)