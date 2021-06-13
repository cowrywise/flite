from rest_framework import viewsets, mixins
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Balance, User, NewUserPhoneVerification, Transaction
from .permissions import IsUserOrReadOnly
from rest_framework.permissions import IsAuthenticated
from .serializers import (CreateUserSerializer, UserSerializer, SendNewPhonenumberSerializer,
                          DepositWithdrawalSerializer, TransactionSerializer)
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView, ListAPIView
from . import utils
from rest_framework.decorators import action
from rest_framework.validators import ValidationError
from rest_framework.pagination import PageNumberPagination

from django.db.models import F
from rest_framework import status

class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """
    Updates and retrieves user accounts
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsUserOrReadOnly,)

    @action(detail=True, methods=['post'])
    def withdrawals(self, request, pk=None):
        user = self.get_object()
        serializer = DepositWithdrawalSerializer(data=request.data)

        if serializer.is_valid():
            if user:
                amount = serializer.validated_data.get('amount')
                reference = serializer.validated_data.get('reference')
                balance = Balance.objects.filter(owner=user)
                active = list(balance)[0].active
                current_balance = list(balance)[0].available_balance
                if not active:
                    transaction = Transaction(owner=user, reference=reference,
                                              status="Failed - Account Not Active", amount=amount,
                                              new_balance=current_balance)
                    transaction.save()
                    return Response({"message": "User account not active"}, status=status.HTTP_403_FORBIDDEN)
                if list(balance)[0].available_balance < amount:
                    # log transaction even though it failed.
                    transaction = Transaction(owner=user, reference=reference,
                                              status="Failed - Insufficient Funds", amount=amount,
                                              new_balance=current_balance)
                    transaction.save()
                    return Response({"message": "Cannot withdraw more than available balance"},
                                    status=status.HTTP_400_BAD_REQUEST)

                balance.update(available_balance=F('available_balance') - amount)
                balance.update(book_balance=F('book_balance') - amount)
                # log into transaction
                new_bal = list(balance)[0].available_balance
                transaction = Transaction(owner=user, reference=reference,
                                          status="Completed", amount=amount, new_balance=new_bal)
                transaction.save()
                return Response(data={"message": "Deposit Successful", "New Balance": new_bal})
            return Response(data={"message": "user not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(data={"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def deposits(self, request, pk=None):
        user = self.get_object()
        serializer = DepositWithdrawalSerializer(data=request.data)

        if serializer.is_valid():
            if user:
                amount = serializer.validated_data.get('amount')
                reference = serializer.validated_data.get('reference')
                balance = Balance.objects.filter(owner=user)
                active = list(balance)[0].active
                current_balance = list(balance)[0].available_balance
                if not active:
                    transaction = Transaction(owner=user, reference=reference,
                                              status="Failed - Account Not Active", amount=amount,
                                              new_balance=current_balance)
                    transaction.save()
                    return Response({"message": "User account not active"}, status=status.HTTP_403_FORBIDDEN)

                balance.update(available_balance=F('available_balance') + amount)
                balance.update(book_balance=F('book_balance') + amount)
                # log into transaction
                new_bal = list(balance)[0].available_balance
                transaction = Transaction(owner=user, reference=reference,
                                          status="Completed", amount=amount, new_balance=new_bal)
                transaction.save()
                return Response(data={"message": "Deposit Successful", "New Balance": new_bal})
            return Response(data={"message": "user not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(data={"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class UserCreateViewSet(mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    """
    Creates user accounts
    """
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = (AllowAny,)


class SendNewPhonenumberVerifyViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin,
                                      viewsets.GenericViewSet):
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

class P2PTransferViewSet(APIView):
    permission_classes = (IsUserOrReadOnly, IsAuthenticated,)

    def get_objects(self):
        try:
            sender = Balance.objects.get(owner_id=self.kwargs['sender_account_id'])
        except Balance.DoesNotExist:
            raise ValidationError('Invalid Sender')

        try:
            recipient = Balance.objects.get(owner_id=self.kwargs['recipient_account_id'])
        except Balance.DoesNotExist:
            raise ValidationError('Invalid Recipient')
        return sender, recipient

    def post(self, request, *args, **kwargs):
        sender, recipient = self.get_objects()

        amt_serializer = DepositWithdrawalSerializer(data=request.data)
        if amt_serializer.is_valid():
            amount = amt_serializer.validated_data.get('amount')
            reference = amt_serializer.validated_data.get('reference')

            # user cannot transfer to themselves.
            if sender.pk == recipient.pk:
                return Response(data={"message": "Cannot send funds to yourself"},
                                status=status.HTTP_404_NOT_FOUND)
            # user cannot transfer amount more than whats in account.
            if sender.available_balance < amount:
                transaction = Transaction(owner=sender.owner, reference=reference,
                                          status="Failed", amount=amount,
                                          new_balance=sender.available_balance)
                transaction.save()
                return Response({"message": "Cannot transfer more than available balance"},
                                status=status.HTTP_400_BAD_REQUEST)
            # inactive user cannot send funds.
            if not sender.active:
                transaction = Transaction(owner=sender.owner, reference=reference,
                                          status="Failed - Account Not Active", amount=amount,
                                          new_balance=sender.available_balance)
                transaction.save()

            # debit sender account
            sender.available_balance = F('available_balance') - amount
            sender.book_balance = F('book_balance') - amount

            recipient.available_balance = F('available_balance') + amount
            recipient.book_balance = F('book_balance') + amount

            # save new balance in db
            sender.save()
            recipient.save()

            # referesh from db
            sender.refresh_from_db()
            recipient.refresh_from_db()

            # log to transaction for sender
            sender_transaction = Transaction(owner=sender.owner, reference=reference,
                                             status="Completed", amount=amount,
                                             new_balance=sender.available_balance)
            sender_transaction.save()
            #  log to transaction for recipient
            recipient_transaction = Transaction(owner=recipient.owner, reference=reference,
                                                status="Completed", amount=amount,
                                                new_balance=recipient.available_balance)
            recipient_transaction.save()
            return Response(data={"message": "Transfer Done"}, status=status.HTTP_200_OK)
        return Response(data={"message": amt_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class TransactionListViewSet(ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = (IsUserOrReadOnly, IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        paginator = PageNumberPagination()
        paginator.page_size = 100

        user = get_object_or_404(User, id=self.kwargs['account_id'])
        if str(request.user.id) != str(user.id):
            return Response(data={"message": "Only owners can view transaction."},
                            status=status.HTTP_403_FORBIDDEN)
        transactions = self.get_queryset().filter(owner=user)
        results_page = paginator.paginate_queryset(transactions, request)
        serializer = self.serializer_class(results_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class TransactionDetailsViewSet(RetrieveAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = (IsUserOrReadOnly, IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=self.kwargs['account_id'])
        try:
            transaction = self.get_queryset().get(owner=user, id=self.kwargs['transaction_id'])
            serializer = TransactionSerializer(transaction)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except Transaction.DoesNotExist:
            return Response(data={"message": "Such transaction Does not Exist."},
                            status=status.HTTP_404_NOT_FOUND)
