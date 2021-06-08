from rest_framework import mixins, viewsets, status, generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from flite.users.models import Transaction, P2PTransfer
from flite.users.permissions import IsUserTransactionOnly
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
                    "detail": "You do not have permission to perform this action."},
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
                    "detail": "You do not have permission to perform this action."
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
                    "detail": "You do not have permission to perform this action."
                },
                status=status.HTTP_403_FORBIDDEN)
        return super(FetchPaginatedTransactionsForUserViewSet, self).list(request, *args, **kwargs)


class FetchSingleTransactionsForUserView(generics.RetrieveAPIView):
    """
    single user transactions
    """
    queryset = Transaction.objects.all()
    serializer_class = BaseTransactionSerializer
    permission_classes = (IsAuthenticated, IsUserTransactionOnly,)
    lookup_fields = ['account_id', 'transaction_id']

    def get_object(self):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        filter_object = {}
        filter_mapping = {"account_id": "owner__id", "transaction_id": "id"}
        for field in self.lookup_fields:
            if self.kwargs.get(field):
                filter_object[filter_mapping.get(field)] = self.kwargs[field]
        obj = get_object_or_404(queryset, **filter_object)
        self.check_object_permissions(self.request, obj)
        return obj
