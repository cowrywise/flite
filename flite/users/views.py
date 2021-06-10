from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from .models import User, NewUserPhoneVerification
from flite.core.permissions import IsUserOrReadOnly
from .serializers import CreateUserSerializer, \
    UserSerializer, SendNewPhonenumberSerializer
from rest_framework.views import APIView
from flite.account.serializers import DepositSerializer, \
    WithdrawalSerializer
from flite.account.models import Account
from flite.account.services import AccountService


from . import utils


class UserViewSet(viewsets.ModelViewSet):
    """
    Updates and retrieves user accounts
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsUserOrReadOnly,)


    def get_permissions(self):
        if self.action in ["list", "retrieve", "Update"]:
            permission_classes = self.permission_classes
        elif self.action in ["create"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == "create":
            return CreateUserSerializer
        return self.serializer_class

    @action(
        detail=True,
        methods=['post'],
        url_path="deposits",
        serializer_class=DepositSerializer
    )
    def deposit(self, request, pk=None, name='user-deposit'):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            account = AccountService.create_deposit_transaction(
                serializer.validated_data,
                request.user
            )
            return Response(data={
                    "message": "Deposit was successfull",
                    "balance": account}, status=status.HTTP_201_CREATED)
        return Response(data={"message": serializer.errors}, status=422)
    
    @action(
        detail=True,
        methods=['post'],
        url_path="withdrawals",
        serializer_class=WithdrawalSerializer
    )
    def withdrawal(self, request, pk=None, name='user-withdrawal' ):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            try:
                account = AccountService.create_withdraw_transaction(
                    serializer.validated_data,
                    request.user)
                return Response(data={
                    "message": "Deposit was successfull",
                    "balance": account}, status=201)
            except Exception as Ex:              
                return Response(
                        data={
                            "message": f"{Ex}",
                            "balance": AccountService.get_user_serialized_account(request.user)},
                        status=422)
        return Response(data={"message": serializer.errors}, status=422)


class SendNewPhonenumberVerifyViewSet(
    mixins.CreateModelMixin, mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    """
    Sending of verification code
    """
    queryset = NewUserPhoneVerification.objects.all()
    serializer_class = SendNewPhonenumberSerializer
    permission_classes = (AllowAny,)
