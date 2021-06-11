from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import User, NewUserPhoneVerification, Balance, Transaction
from .permissions import IsUserOrReadOnly
from .serializers import CreateUserSerializer, UserSerializer, SendNewPhonenumberSerializer, AmountSerializer
from rest_framework.views import APIView
from rest_framework.decorators import action
from . import utils
from flite.users import serializers
from django.db.models import F


class UserViewSet(
        mixins.RetrieveModelMixin,
        mixins.ListModelMixin,
        mixins.UpdateModelMixin,
        viewsets.GenericViewSet):
    """
    Updates and retrieves user accounts
    """
    queryset = User.objects.all().order_by('username')
    serializer_class = UserSerializer
    permission_classes = (IsUserOrReadOnly,)


    @action(detail=True, methods=['post'])
    def deposits(self, request, pk=None):
        user = self.get_object()
        serializer = AmountSerializer(data=request.data)

        if serializer.is_valid():
            if user:
                amount = serializer.validated_data.get('amount')
                b = Balance.objects.filter(owner=user)
                b.update(book_balance=F('book_balance') + amount)
                b.update(available_balance=F('available_balance') + amount)

                new_balance = list(b)[0].available_balance
                # Add to transaction table transaction 
                utils.log_transaction(
                    user=user,
                    reference=utils.generate_transaction_refrence_code(),
                    status=utils.COMPLETED,
                    type=utils.CREDIT,
                    amount=amount,
                    new_balance=new_balance
                )
                
                return Response(data={
                    "message": "Deposit Successful"
                })
            return Response(data={"message: user not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(data= {"message": serializer.errors['amount'][0]}, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=['post'])
    def withdrawals(self, request, pk=None):
        user = self.get_object()
        account_serializer = AmountSerializer(data=request.data)

        if account_serializer.is_valid():
            if user:
                amount = account_serializer.validated_data.get('amount')
                balance_before_withrawal = utils.check_balance(user) 
                if balance_before_withrawal < amount or balance_before_withrawal == 0:
                    return Response(data={"message": "Insufficient funds"}, status=status.HTTP_403_FORBIDDEN) 
                
                b = Balance.objects.filter(owner=user)
                b.update(book_balance=F('book_balance') - amount)
                b.update(available_balance=F('available_balance') - amount)
                
                new_balance = list(b)[0].available_balance
                
                utils.log_transaction(
                    user=user,
                    reference=utils.generate_transaction_refrence_code(),
                    status=utils.COMPLETED,
                    type=utils.DEBIT,
                    amount=amount,
                    new_balance=new_balance
                )
            return Response(data={
                    "message": "Withdrawal Successful"
                })
        return Response(data= {"message": account_serializer.errors['amount'][0]}, status=status.HTTP_400_BAD_REQUEST)


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
