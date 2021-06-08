from rest_framework import mixins, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from flite.users.models import Transaction, P2PTransfer
from flite.users.serializers import (
    CreateDepositSerializer,
    CreateWithdrawalSerializer,
    PeerToPeerTransferSerializer
)


class BaseDepositWithdrawalViewSet(mixins.CreateModelMixin,
                                   viewsets.GenericViewSet):
    queryset = Transaction.objects.all()
    serializer_class = None
    permission_classes = []

    def custom_create(self, kwargs, request):
        serializer = self.get_serializer(data=request.data)
        serializer.context["user_id"] = kwargs.get('user_id', None)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)


class DepositViewSet(BaseDepositWithdrawalViewSet):
    """
    Creates a deposit into a user account
    """
    queryset = Transaction.objects.all()
    serializer_class = CreateDepositSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        return self.custom_create(kwargs, request)


class WithdrawalViewSet(BaseDepositWithdrawalViewSet):
    """
    Makes a withdrawal from a user account
    """
    queryset = Transaction.objects.all()
    serializer_class = CreateWithdrawalSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        owner_id = kwargs.get('user_id', None)
        request_user = request.user
        if str(request_user.id) != owner_id:
            return Response(
                {
                    "detail": "Permission denied, you cant withdraw from another account, "
                              "kindly withdraw from your own account"},
                status=status.HTTP_403_FORBIDDEN)
        return self.custom_create(kwargs, request)


class PeerToPeerTransferViewSet(mixins.CreateModelMixin,
                                viewsets.GenericViewSet):
    queryset = P2PTransfer.objects.all()
    serializer_class = PeerToPeerTransferSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        request_user = request.user
        owner_id = kwargs.get('sender_account_id', None)
        if str(request_user.id) != owner_id:
            return Response(
                {
                    "detail": "Permission denied, you cant transfer from another account, "
                              "kindly transfer from your own account"
                },
                status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data)
        serializer.context["sender_account_id"] = owner_id
        serializer.context["recipient_account_id"] = kwargs.get('recipient_account_id', None)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)
