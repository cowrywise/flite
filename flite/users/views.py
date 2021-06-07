from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User, NewUserPhoneVerification
from .permissions import IsUserOrReadOnly
from .serializers import *
from rest_framework.views import APIView
from . import utils

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


class DepositViewSet(mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    """
    ViewSet For Deposits
    """
    queryset = Transaction.objects.all()
    serializer_class = DepositSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        response_serializer = BalanceSerializer(instance)
        headers = self.get_success_headers(response_serializer.data)
        return Response(
            response_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

class WithdrawalViewSet(mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    """
    ViewSet For Withdrawals
    """
    queryset = Transaction.objects.all()
    serializer_class = WithdrawalSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        response_serializer = BalanceSerializer(instance)
        headers = self.get_success_headers(response_serializer.data)
        return Response(
            response_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

class TransferViewSet(mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    """
    Creates user accounts
    """
    queryset = Transaction.objects.all()
    serializer_class = TransferSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post']

    #def create(self, request, *args, **kwargs):
    #  serializer = self.get_serializer(data=request.data)
    #  serializer.is_valid(raise_exception=True)
    #  #self.perform_create(serializer)
    #  headers = self.get_success_headers(serializer.data)
    #  return Response(
    #    serializer.data, status=status.HTTP_201_CREATED, headers=headers
    #  )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sender_account_id = self.kwargs.get("sender_account_id")
        recipient_account_id = self.kwargs.get("recipient_account_id")
        sender = request.user
        try:
            recipient = User.objects.get(id=recipient_account_id)
        except User.DoesNotExist:
            return Response({"details": "Recipient Account Not Found"}, status.HTTP_404_NOT_FOUND)
        sender_balance = Balance.objects.get(owner=sender)
        recipient_balance = Balance.objects.get(owner=recipient)
        #Todo: Check If The Accounts are Active
        amount = request.data.get("amount")

        #Debit The sender
        sender_balance.book_balance = F('book_balance') - amount
        sender_balance.available_balance = F('available_balance') - amount
        sender_transfer_transaction = P2PTransfer(
            sender=sender, 
            recipient=recipient, 
            amount=amount, 
            owner=sender,
            status="success",
            new_balance=sender_balance.book_balance
        )
        sender_balance.save()
        sender_transfer_transaction.save()

        #Credit The Recipient
        recipient_balance.book_balance = F('book_balance') + amount
        recipient_balance.available_balance = F('available_balance') + amount
        recipient_transfer_transaction = P2PTransfer(
            sender=sender, 
            recipient=recipient, 
            amount=amount, 
            owner=recipient,
            status="success",
            new_balance=recipient_balance.book_balance
        )
        recipient_balance.save()
        recipient_transfer_transaction.save()

        #return Sender Balance
        return_serializer = BalanceSerializer(sender_balance)
        headers = self.get_success_headers(return_serializer.data)
        return Response(
            return_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )