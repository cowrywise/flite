from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User, NewUserPhoneVerification
from .permissions import IsUserOrReadOnly
from .serializers import *
from rest_framework.views import APIView
from rest_framework.decorators import api_view
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

class TransactionViewSet(mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """
    Updates and retrieves user accounts
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = super().get_queryset() 
        return queryset.filter(owner=self.request.user)

@api_view(["GET"])
def transaction_detail(request, account_id, pk):
    try:
        transaction = P2PTransfer.objects.get(id=pk)
        if transaction.owner != request.user:
            return Response({"details": "Not Permitted"}, status.HTTP_403_FORBIDDEN)
        serializer = P2PTransferSerializer(transaction)
        return Response(serializer.data)
    except P2PTransfer.DoesNotExist:
        try:
            transaction = Transaction.objects.get(id=pk)
            if transaction.owner != request.user:
                return Response({"details": "Not Permitted"}, status.HTTP_403_FORBIDDEN)
            serializer = TransactionSerializer(transaction)
            return Response(serializer.data)
        except Transaction.DoesNotExist:
            return Response({"details": "Transaction Details Not Found"}, status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        print(e)
        return Response({"details": "An Error Occurred. Try Again"}, status.HTTP_400_BAD_REQUEST)


class TransferViewSet(mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    """
    Creates user accounts
    """
    queryset = Transaction.objects.all()
    serializer_class = TransferSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):

        """
        Checks if Recipient Account Exists
        sender is the same as the user sending the request
        removes amount from sender's account
        adds amount to receipient's account
        saves a P2PTransfer Object for both sender and recipient
        returns the sender balance.
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sender_account_id = self.kwargs.get("sender_account_id")
        receipient_account_id = self.kwargs.get("receipient_account_id")
        sender = request.user
        try:
            sender_from_url = User.objects.get(id=sender_account_id)
            if sender_from_url != sender:
                return Response({"details": "Not Permitted"}, status.HTTP_403_FORBIDDEN)
        except User.DoesNotExist:
            return Response({"details": "Sender Account Not Found"}, status.HTTP_404_NOT_FOUND)

        try:
            receipient = User.objects.get(id=receipient_account_id)
        except User.DoesNotExist:
            return Response({"details": "Recipient Account Not Found"}, status.HTTP_404_NOT_FOUND)
        sender_balance = Balance.objects.get(owner=sender)
        receipient_balance = Balance.objects.get(owner=receipient)
        amount = request.data.get("amount")

        #Debit The sender
        sender_balance.book_balance = F('book_balance') - amount
        sender_balance.available_balance = F('available_balance') - amount
        sender_balance.save()
        sender_balance.refresh_from_db()
        sender_transfer_transaction = P2PTransfer(
            sender=sender, 
            receipient=receipient, 
            amount=amount, 
            owner=sender,
            status="success",
            new_balance=sender_balance.book_balance
        )
        sender_transfer_transaction.save()

        #Credit The Recipient
        receipient_balance.book_balance = F('book_balance') + amount
        receipient_balance.available_balance = F('available_balance') + amount
        receipient_balance.save()
        receipient_balance.refresh_from_db()
        receipient_transfer_transaction = P2PTransfer(
            sender=sender, 
            receipient=receipient, 
            amount=amount, 
            owner=receipient,
            status="success",
            new_balance=receipient_balance.book_balance
        )
        
        receipient_transfer_transaction.save()

        #return Sender Balance
        return_serializer = BalanceSerializer(sender_balance)
        headers = self.get_success_headers(return_serializer.data)
        return Response(
            return_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )