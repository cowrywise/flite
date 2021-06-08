from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render

from flite.transfers.models import Transaction
from flite.transfers.serializers import P2PTransferSerializer, TransferSerializer
from flite.transfers.wallets import UserWallet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

User = get_user_model()


class AccountsViewSet(viewsets.ModelViewSet):
    model = User
    serializer_class = P2PTransferSerializer

    def get_queryset(self):
        return self.model.objects.all()

    def list(self, request):
        return Response({"message": "nothing to see here"})

    @action(
        detail=True,
        methods=["POST"],
        url_path="transfers/(?P<recipient>[^/.]+)",
    )
    def transfers(self, request, recipient=None, pk=None):
        """
        end point allows users to send funds from own account
        to another
        """
        user = self.get_object()
        serializer = self.get_serializer(
            data={**request.data, "sender": pk, "recipient": recipient},
            exclude=["owner", "reference", "status"],
        )
        if serializer.is_valid():
            transfer = UserWallet.p2p_transfer(**serializer.validated_data)
            data = self.get_serializer(
                transfer, exclude=["sender", "recipient", "owner"]
            ).data

            return Response(
                {"success": True, "message": "success", "data": data},
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

    @action(detail=True, methods=["GET"], serializer_class=TransferSerializer)
    def transactions(self, request, pk=None):
        """returns a list of transactions carried out by users"""
        queryset = Transaction.objects.filter(owner=request.user).order_by("created")
        page = self.paginate_queryset(queryset)
        serializer = self.serializer_class(page, many=True, exclude=["owner"])
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=["GET"],
        url_path="transactions/(?P<transaction_id>[^/.]+)",
        url_name="single_transaction",
        serializer_class=TransferSerializer,
    )
    def transaction(self, request, transaction_id=None, pk=None):
        """gets a single user specific transaction"""
        queryset = Transaction.objects.filter(owner=request.user)
        obj = get_object_or_404(queryset, id=transaction_id)
        serializer = self.get_serializer(obj, exclude=["owner"])
        return Response(
            {"success": True, "message": "success", "data": serializer.data},
            status=status.HTTP_200_OK,
        )
