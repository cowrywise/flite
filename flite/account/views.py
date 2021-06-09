
from rest_framework import viewsets
from rest_framework.response import Response
from .models import AllBanks, Bank, Card, CardTransfer, P2PTransfer, \
    BankTransfer, User
from flite.core.permissions import IsUserOrReadOnly
from .serializers import AllBanksSerializer, BankSerializer, \
    CardSerializer, CardTransferSerializer, P2PTransferSerializer, \
    BankTransferSerializer
from .utils import randomStringDigits



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
    serializer_class = BankTransferSerializer
    permission_classes = [IsUserOrReadOnly]