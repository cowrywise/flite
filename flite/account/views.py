
from rest_framework import viewsets
from rest_framework.response import Response
from .models import AllBanks, Bank
from flite.core.permissions import IsUserOrReadOnly
from .serializers import AllBanksSerializer, BankSerializer



class BankViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing Banks.
    """
    serializer_class = BankSerializer
    permission_classes = [IsUserOrReadOnly]

    def get_queryset(self):
        return Bank.objects.filter(owner=self.request.user)