from django.shortcuts import get_object_or_404

from flite.banks.manager import AccountManager
from flite.banks.serializers import BankSerializer
from flite.transfers.serializers import BankWithdrawalSerializer, BankDepositSerializer
from flite.transfers.wallets import UserWallet
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import utils
from .models import NewUserPhoneVerification, User
from .permissions import IsUserOrReadOnly
from .serializers import (
    CreateUserSerializer,
    SendNewPhonenumberSerializer,
    UserSerializer,
)


class UserViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """
    view handles retriving updating, listing and creating
    a users account as well as getting a list of banks
    a user registers. This viewset also handles withdrawals
    and deposits to and from the bank.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsUserOrReadOnly,)

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

    def create(self, request, *args, **kwarg):
        return mixins.CreateModelMixin.create(self, request, *args, **kwarg)

    @action(detail=False, methods=["GET"])
    def registered_banks(self, request):
        """all banks belonging to the user"""
        accounts = AccountManager.all_accounts(user=request.user)
        serializer = BankSerializer(accounts, many=True)
        return Response(
            {
                "success": True,
                "message": "successful",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["POST"], serializer_class=BankDepositSerializer)
    def deposits(self, request, pk=None):
        """enables user deposit into wallet"""
        user = self.get_object()
        serializer = self.get_serializer(data=request.data, exclude=["owner"])
        if serializer.is_valid():
            deposit = UserWallet.receive_bank_deposit(
                user=user, **serializer.validated_data
            )
            return Response(
                {
                    "success": True,
                    "message": "successful",
                    "data": self.get_serializer(deposit).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "message": "failed",
                "data": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=True, methods=["POST"], serializer_class=BankWithdrawalSerializer)
    def withdrawals(self, request, pk=None):
        """enables user withdraw to bank"""
        user = self.get_object()
        serializer = self.get_serializer(data=request.data, exclude=["owner"])
        if serializer.is_valid():
            withdrawal = UserWallet.withdraw_to_bank(
                user=user, **serializer.validated_data
            )
            return Response(
                {
                    "success": True,
                    "message": "successful",
                    "data": self.get_serializer(withdrawal).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "message": "failed",
                "data": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class SendNewPhonenumberVerifyViewSet(
    mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):
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

        code_status, msg = utils.validate_mobile_signup_sms(
            verification_object.phone_number, code
        )

        content = {
            "verification_code_status": str(code_status),
            "message": msg,
        }
        return Response(content, 200)
