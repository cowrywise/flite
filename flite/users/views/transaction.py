from rest_framework import mixins, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from flite.users.models import Transaction, P2PTransfer
from flite.users.serializers import (
    CreateDepositSerializer,
    CreateWithdrawalSerializer,
    PeerToPeerTransferSerializer,
    BaseTransactionSerializer
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


class FetchPaginatedTransactionsForUserViewSet(mixins.ListModelMixin,
                                               viewsets.GenericViewSet):
    """
    List user transactions
    """
    queryset = Transaction.objects.all()
    serializer_class = BaseTransactionSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = 'account_id'

    def get_queryset(self):
        if self.lookup_field is None:
            return None
        request_account_id = self.kwargs[self.lookup_field]
        val = Transaction.objects.filter(owner__id=request_account_id)
        return val

    def list(self, request, *args, **kwargs):
        request_user = request.user
        owner_id = kwargs.get('account_id', None)
        if str(request_user.id) != owner_id:
            return Response(
                {
                    "detail": "Permission denied, you can't view transactions belonging to another user"
                },
                status=status.HTTP_403_FORBIDDEN)
        return super(FetchPaginatedTransactionsForUserViewSet, self).list(request, *args, **kwargs)
