from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from flite.core.permissions import IsUserOrReadOnly, IsOwnerOnly

from .models import (Bank, BankTransfer, Card, CardTransfer, P2PTransfer,
                     Transaction)
from .serializers import (AccountSerializer, BankSerializer,
                          BankTransferSerializer, CardSerializer,
                          CardTransferSerializer, P2PTransferSerializer,
                          TransactionSerializer, TransferSerializer)
from .services import AccountService
from .utils import randomStringDigits


class BankViewSet(viewsets.ModelViewSet):
    """
    A Bank ViewSet with GET, POST, UPDATE and DELETE method.
    """
    serializer_class = BankSerializer
    permission_classes = [IsOwnerOnly]

    def get_queryset(self):
        return Bank.objects.filter(owner=self.request.user)


class CardViewSet(viewsets.ModelViewSet):
    """
    A Card ViewSet with GET, POST, UPDATE and DELETE method
    """
    serializer_class = CardSerializer
    permission_classes = [IsOwnerOnly]

    def get_queryset(self):
        return Card.objects.filter(owner=self.request.user)


class CardTransferViewSet(viewsets.ModelViewSet):
    """
    A Card Transfer ViewSet with GET, POST, UPDATE and DELETE method
    """
    serializer_class = CardTransferSerializer
    permission_classes = [IsOwnerOnly]

    def get_queryset(self):
        return CardTransfer.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(reference=randomStringDigits())


class P2PTransferViewSet(viewsets.ModelViewSet):
    """
    A Peer-toper Transfer ViewSet with GET, POST, UPDATE and DELETE method
    """

    serializer_class = P2PTransferSerializer
    permission_classes = [IsOwnerOnly]

    def get_queryset(self):
        return P2PTransfer.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(reference=randomStringDigits())


class BankTransferViewSet(viewsets.ModelViewSet):
    """
    A Bank Transfer ViewSet with GET, POST, UPDATE and DELETE method
    """

    serializer_class = BankTransferSerializer
    permission_classes = [IsOwnerOnly]

    def get_queryset(self):
        return BankTransfer.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(reference=randomStringDigits())


class AccountViewSet(viewsets.GenericViewSet):
    """An account ViewSet.

    Methods:
        transfers: This actions handles peer-to-peer
            transfer transaction. The authenticated user
            is sender sender of the funds.
        transactions: This action returns all the transactions
            of the authenticated user.
        transaction: This actions handles the return of a
            single transaction
    """

    serializer_class = AccountSerializer
    permission_classes = [IsUserOrReadOnly]

    @action(detail=True,
            methods=["POST"],
            url_path="transfers/(?P<receipient_account_id>[^/.]+)",
            serializer_class=TransferSerializer)
    def transfers(
        self,
        request,
        pk=None,
        receipient_account_id=None,
    ):
        """Handles p2p transactions. This method requires the receipient
        account id and sender account id as path parameters."""

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data.get('amount')
            try:
                account = AccountService.transfer(request.user,
                                                  receipient_account_id,
                                                  amount)
                return Response(
                    data={
                        "message": "Your transfer was successful",
                        "balance": account
                    },
                    status=202,
                )
            except Exception as Ex:

                return Response(data={
                    "message":
                    f"{Ex}",
                    "balance":
                    AccountService.get_user_serialized_account(request.user)
                }, status=422)
        return Response(data={"message": serializer.errors}, status=422)

    @action(detail=True,
            url_path="transactions",
            serializer_class=TransactionSerializer,
            queryset=Transaction.objects.all())
    def transactions(
        self,
        request,
        pk=None,
    ):
        """Returns all transaction of authenticated user. This action
        requires user account id as path parameter"""
        queryset = Transaction.objects.filter(owner=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        url_path="transactions/(?P<transaction_id>[^/.]+)",
    )
    def transaction(
        self,
        request,
        pk=None,
        transaction_id=None,
    ):
        """Returns a detail transaction. This action requires user account
        id and transaction id as path parameters"""
        try:
            data = AccountService.get_transaction(transaction_id, pk)
            return Response(data.data)
        except Exception as Ex:
            return Response(data={"message": f"{Ex}"}, status=422)
