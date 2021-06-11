from rest_framework import viewsets, mixins
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from .models import User, NewUserPhoneVerification, Balance, Card, Transaction, AllBanks, BankAccount
from .permissions import IsUserOrReadOnly
from .serializers import CreateUserSerializer, UserSerializer, SendNewPhonenumberSerializer, BalanceSerializer, \
    CreateBankAccountSerializer, TransferSerializer, WithdrawFundsSerializer, TransactionSerializer, \
    FundAccountSerializer, BanksSerializer
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated, AllowAny
from . import utils
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView
from django.utils.crypto import get_random_string


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """
    Updates and retrieves user accounts
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


@csrf_exempt
@api_view(['GET', ])
@permission_classes([])
@authentication_classes([])
def get_balance(request, user_id):
    if request.method == 'GET':
        try:
            balance = Balance.objects.get(owner=user_id)
        except Balance.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = BalanceSerializer(balance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateBankAccountView(CreateAPIView):
    serializer_class = CreateBankAccountSerializer
    queryset = BankAccount.objects.all()
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated, ]

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)


class BankList(ListAPIView):
    queryset = AllBanks.objects.all().order_by('name')
    serializer_class = BanksSerializer
    authentication_classes = (BasicAuthentication,)
    permission_classes = ()
    pagination_class = PageNumberPagination


class AllAccountTransactions(RetrieveAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransferSerializer
    authentication_classes = (BasicAuthentication,)
    permission_classes = ()
    pagination_class = PageNumberPagination

    def get(self, *args, **kwargs):
        balance = kwargs['balance_id']
        return JsonResponse(data=list(Transaction.objects.filter(balance=balance).order_by('-date_created').select_related('owner',
                                                                                                            'balance').values()), safe=False)


class ViewAccountTransaction(RetrieveAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransferSerializer
    authentication_classes = (BasicAuthentication,)
    permission_classes = ()
    pagination_class = PageNumberPagination

    def get(self, *args, **kwargs):
        transaction = kwargs['transaction_id']
        balance = kwargs['balance_id']
        transactions = Transaction.objects.filter(balance=balance).values()
        single_transaction = transactions.get(id=transaction)
        return JsonResponse(data=single_transaction, safe=False)


@csrf_exempt
@api_view(['POST', ])
@permission_classes([])
@authentication_classes([])
def fund_account(request, user_id):
    if request.method == 'POST':
        receiver = User.objects.get(id=user_id)
        receiver_account = Balance.objects.get(owner=receiver.id)
        data = {'reference': get_random_string(), 'amount': request.data['amount']}
        transaction = Transaction.objects.create(owner=receiver, amount=float(request.data['amount']),
                                                 reference=data['reference'], status='FAILED',
                                                 transaction_type='Fund Account', balance=receiver_account, )
        transaction.save()
        serializer = FundAccountSerializer(data=data)
        if serializer.is_valid():
            serializer.save(receiver=receiver, status='SUCCESS')
            Transaction.objects.create(owner=receiver, amount=float(request.data['amount']), reference=data['reference'],
                                       status='SUCCESS', transaction_type='Fund Account', balance=receiver_account, )
            receiver_account.available_balance += float(request.data['amount'])
            receiver_account.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST', ])
@permission_classes([IsAuthenticated])
@authentication_classes([BasicAuthentication])
def transfer_funds(request, sender_balance_id, receiver_balance_id):
    if request.method == 'POST':
        sender_account = Balance.objects.get(id=sender_balance_id)
        receiver_account = Balance.objects.get(id=receiver_balance_id)
        sender = User.objects.get(id=sender_account.owner.id)
        receiver = User.objects.get(id=sender_account.owner.id)
        data = {'reference': get_random_string(),
                'transfer_type': request.data['transfer_type'], 'amount': request.data['amount']}
        if float(request.data['amount']) > sender_account.available_balance:
            Transaction.objects.create(owner=sender, amount=float(request.data['amount']), reference=data['reference'],
                                       status='FAILED', transaction_type='Transfer(P2P)', balance=sender_account, )
            return Response({'error': 'You cant transfer than your available balance'},
                            status=status.HTTP_406_NOT_ACCEPTABLE)
        serializer = TransferSerializer(data=data)
        if serializer.is_valid():
            serializer.save(sender=sender, status='SUCCESS', receiver=receiver)
            sender_account.available_balance -= float(request.data['amount'])
            receiver_account.available_balance += float(request.data['amount'])
            sender_account.save()
            receiver_account.save()
            sender_transaction = Transaction.objects.create(owner=sender, amount=float(request.data['amount']),
                                                            reference=data['reference'], status='SUCCESS',
                                                            transaction_type='Transfer(P2P)', balance=sender_account,)
            sender_transaction.save()
            receiver_transaction = Transaction.objects.create(owner=sender, amount=float(request.data['amount']),
                                                              reference=data['reference'], status='SUCCESS',
                                                              transaction_type='Transfer(P2P)', balance=receiver_account,)
            receiver_transaction.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST', ])
@permission_classes([IsAuthenticated])
@authentication_classes([BasicAuthentication])
def withdraw_funds(request, user_id):
    if request.method == 'POST':
        owner = User.objects.get(id=user_id)
        receiver_account = Balance.objects.get(owner=owner)
        data = {'reference': get_random_string(), 'amount': request.data['amount']}
        if float(request.data['amount']) > receiver_account.available_balance:
            Transaction.objects.create(owner=owner, amount=float(request.data['amount']), reference=data['reference'],
                                       status='FAILED', transaction_type='Withdraw', balance=receiver_account)
            return Response({'error': 'Check amount entered'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        serializer = WithdrawFundsSerializer(data=data)
        if serializer.is_valid():
            serializer.save(receiver=owner, status='SUCCESS')
            receiver_account.available_balance -= float(request.data['amount'])
            receiver_account.save()
            Transaction.objects.create(owner=owner, amount=float(request.data['amount']), reference=data['reference'],
                                       status='SUCCESS', transaction_type='Withdraw', balance=receiver_account)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)