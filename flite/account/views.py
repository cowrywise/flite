
from rest_framework import viewsets
from rest_framework.response import Response
from .models import AllBanks, Bank, Card, CardTransfer
from flite.core.permissions import IsUserOrReadOnly
from .serializers import AllBanksSerializer, BankSerializer, \
    CardSerializer, CardTransferSerializer



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