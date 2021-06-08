from django.db import transaction as db_transaction
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from .models import User, NewUserPhoneVerification, Balance
from flite.core.permissions import IsUserOrReadOnly
from .serializers import CreateUserSerializer, \
    UserSerializer, SendNewPhonenumberSerializer, BalanceSerializer
from rest_framework.views import APIView
from flite.account.serializers import DepositSerializer
from flite.account.services import AccountService


from . import utils


class UserViewSet(viewsets.ModelViewSet):
    """
    Updates and retrieves user accounts
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsUserOrReadOnly,)

    @action(
        detail=True,
        methods=['post'],
        url_path="deposit",
        serializer_class=DepositSerializer
    )
    def deposits(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            with db_transaction.atomic():
                balance = Balance.objects.select_for_update().filter(owner=request.user).first()
                balance.available_balance += serializer.validated_data.get('amount')
                balance.book_balance += serializer.validated_data.get('amount')
                AccountService.create_deposit_transaction(
                    serializer.validated_data,
                    request.user
                )

                balance.save()
                balance.refresh_from_db()
                return Response(data={
                    "message": "Deposit was successfull",
                    "balance": BalanceSerializer(balance).data}, status=201)
        return Response(data={"message": serializer.errors}, status=422)


class UserCreateViewSet(mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    """
    Creates user accounts
    """
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = (AllowAny,)


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
