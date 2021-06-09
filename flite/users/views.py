from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import (
    User, NewUserPhoneVerification, Transaction, Balance)
from .permissions import IsUserOrReadOnly
from .serializers import (
    CreateUserSerializer, UserSerializer, SendNewPhonenumberSerializer, 
    TransactionSerializer, P2PTransferSerializer, BalanceSerializer, 
    DepositSerializer, WithdrawSerializer)
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from . import utils
from .pagination import CustomPageNumberPagination
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import generics
from flite.core.helpers.get_response import get_response
from flite.core.helpers.check_resource import resource_exists

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
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    """
    Creates user accounts
    """
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = (AllowAny,)
    pagination_class = CustomPageNumberPagination


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

class UserTransactionViewSet(ViewSet, viewsets.GenericViewSet):
    """ User Transaction ViewSet """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = (IsUserOrReadOnly,)

    def single_transactions(self, request, *args, **kwargs):
        account_id = kwargs.get("pk")
        transaction_id = kwargs.get("transaction_id")
        user = resource_exists(User, {"pk": account_id})
        response_attr = {'error_key': 'not_found'}
        res_status = status.HTTP_404_NOT_FOUND

        if not user:
            return Response(
                get_response(error_key='not_found', format_str='user'),
                status=status.HTTP_404_NOT_FOUND
            )
        
        transaction = resource_exists(Transaction, {"pk": transaction_id, "owner": user})
        if not transaction:
            return Response(
                get_response(error_key='not_found', format_str='transaction'),
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(transaction)

        response_attr = {'res_type': 'success', 'data': serializer.data}
        res_status = status.HTTP_200_OK

        data = get_response(**response_attr)
        return Response(data, status=res_status)
    
    def p2p_transfer(self, request, *args, **kwargs):
        sender_account_id = kwargs.get("sender_account_id")
        receipient_id = kwargs.get("receipient_id")
        sender_account = resource_exists(User, {"pk": sender_account_id})
        receipient = resource_exists(User, {"pk": receipient_id})
        response_attr = {'error_key': 'not_found'}
        if not sender_account:
            return Response(
                get_response(error_key='not_found', format_str='sender'),
                status=status.HTTP_404_NOT_FOUND
            )
        if not receipient:
            return Response(
                get_response(error_key='not_found', format_str='receipient'),
                status=status.HTTP_404_NOT_FOUND
            )
       
        serializer = P2PTransferSerializer(
            data=request.data)
        if serializer.is_valid():
            serializer.save(sender=sender_account, receipient=receipient)
            data = {
                'status': 'success',
                'message': 'Transfer Done Successfully',
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_200_OK)
        data = {
            'status': 'error',
            'data': serializer.errors
        }
        return Response(data, status=status.HTTP_400_BAD_REQUEST)


class DepositWithdrawalViewSet(mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    """
        Deposits and Withdrawal View Set
    """
    queryset = Balance.objects.all()
    serializer_class = BalanceSerializer
    permission_classes = (IsUserOrReadOnly,)
    pagination_class = CustomPageNumberPagination


    @action(methods=['post'], detail=True, permission_classes=[IsUserOrReadOnly],
        url_path='deposits', url_name='users-deposits')
    def deposits(self, request, *args, **kwargs):
        owner_id = kwargs.get("pk")

        owner = resource_exists(User, {"pk": owner_id})
        response_attr = {'error_key': 'not_found'}
        if not owner:
            return Response(
                get_response(error_key='not_found', format_str='user'),
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = DepositSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=owner)
            data = {
                'status': 'success',
                'message': 'Your Deposit Request was Successful',
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_200_OK)
        
        data = {
            'status': 'error',
            'data': serializer.errors
        }
        return Response(data, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=True, permission_classes=[IsUserOrReadOnly],
        url_path='withdrawals', url_name='users-withdrawals')
    def withdrawals(self, request, *args, **kwargs):
        owner_id = kwargs.get("pk")

        owner = resource_exists(User, {"pk": owner_id})
        response_attr = {'error_key': 'not_found'}
        if not owner:
            return Response(
                get_response(error_key='not_found', format_str='user'),
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = WithdrawSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=owner)
            data = {
                'status': 'success',
                'message': 'Your Withdrawal Request was Successfully',
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_200_OK)
        
        data = {
            'status': 'error',
            'data': serializer.errors
        }
        return Response(data, status=status.HTTP_400_BAD_REQUEST)


class UserTransactionAllViewSet(ViewSet, viewsets.GenericViewSet):
    """ User Transaction ViewSet """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = (IsUserOrReadOnly,)
    pagination_class = CustomPageNumberPagination

    @action(methods=['get'], detail=True, permission_classes=[IsUserOrReadOnly],
        pagination_class = CustomPageNumberPagination,
        url_path='transactions', url_name='transactions')
    def transactions(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')
        user = resource_exists(User, {"pk": user_id})
        response_attr = {'error_key': 'not_found'}
        res_status = status.HTTP_404_NOT_FOUND
        if user:
            queryset = self.filter_queryset(self.get_queryset())
            qs = queryset.filter(owner=user)

            page = self.paginate_queryset(qs)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(qs, many=True)
            response_attr = {'res_type': 'success', 'data': serializer.data}
            res_status = status.HTTP_200_OK

        response_attr.update({'format_str': 'transaction'})
        data = get_response(**response_attr)
        return Response(data, status=res_status)

