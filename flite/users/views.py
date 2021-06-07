from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User, NewUserPhoneVerification
from .permissions import IsUserOrReadOnly
from .serializers import (
    CreateUserSerializer,
    UserSerializer,
    SendNewPhonenumberSerializer,
)
from rest_framework.views import APIView
from . import utils
from rest_framework.decorators import action
from flite.transfers.serializers import TransferSerializer
from flite.banks.serializers import BankSerializer
from flite.banks.manager import AccountManager
from flite.transfers.wallets import UserWallet


class UserViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    Updates and retrieves user accounts
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsUserOrReadOnly,)

    def get_permissions(self):
        if self.action in ["list", "retrieve", "Update"]:
            permission_classes = self.permission_classes
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

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

    @action(detail=True, methods=["POST"], serializer_class=TransferSerializer)
    def deposits(self, request, pk=None):
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
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "message": "failed",
                "data": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserCreateViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Creates user accounts
    """

    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = (AllowAny,)


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
