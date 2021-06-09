
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import AllBanks, Bank, Card, CardTransfer, P2PTransfer, \
    BankTransfer, User, Transaction
from flite.core.permissions import IsUserOrReadOnly
from .serializers import AllBanksSerializer, BankSerializer, \
    CardSerializer, CardTransferSerializer, P2PTransferSerializer, \
    BankTransferSerializer, AccountSerializer, TransferSerializer, \
    TransactionSerializer
from .utils import randomStringDigits
from .services import AccountService


class BankViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing Banks.
    """
    serializer_class = BankSerializer
    permission_classes = [IsUserOrReadOnly]

    def get_queryset(self):
        return Bank.objects.filter(owner=self.request.user)


class CardViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing Cards.
    """
    serializer_class = CardSerializer
    permission_classes = [IsUserOrReadOnly]

    def get_queryset(self):
        return Card.objects.filter(owner=self.request.user)


class CardTransferViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing Cards.
    """
    serializer_class = CardTransferSerializer
    permission_classes = [IsUserOrReadOnly]

    def get_queryset(self):
        return CardTransfer.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(reference=randomStringDigits())


class P2PTransferViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing Cards.
    """
    serializer_class = P2PTransferSerializer
    permission_classes = [IsUserOrReadOnly]

    def get_queryset(self):
        return P2PTransfer.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(reference=randomStringDigits())


class BankTransferViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing Cards.
    """
    serializer_class = BankTransferSerializer
    permission_classes = [IsUserOrReadOnly]

    def get_queryset(self):
        return BankTransfer.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(reference=randomStringDigits())


class AccountViewSet(viewsets.GenericViewSet):
    serializer_class = AccountSerializer
    permission_classes = [IsUserOrReadOnly]

    @action(
        detail=True,
        methods=["POST"],
        url_path="transfers/(?P<receipient_account_id>[^/.]+)",
        serializer_class=TransferSerializer
    )
    def transfers(
        self,
        request,
        pk=None,
        receipient_account_id=None,
    ):

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data.get('amount')
            try:
                account = AccountService.transfer(request.user, receipient_account_id, amount)
                return Response(
                    data={"message": "Your transfer was successful",
                          "balance": account},
                    status=201,
                )
            except Exception as Ex:

                return Response(
                    data={
                        "message": f"{Ex}",
                        "balance": AccountService.get_user_serialized_account(request.user)},
                    status=422)
        return Response(data={"message": serializer.errors}, status=422)

    @action(
        detail=True,
        url_path="transactions",
        serializer_class=TransactionSerializer,
        queryset=Transaction.objects.all()
    )
    def transactions(
        self,
        request,
        pk=None,
    ):
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
        try:
            data = AccountService.get_transaction(transaction_id, pk)
            return Response(data.data)
        except Exception as Ex:
            return Response(
                data={"message": f"{Ex}"})
