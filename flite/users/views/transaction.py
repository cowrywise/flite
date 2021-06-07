from rest_framework import mixins, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from flite.users.models import Balance, Transaction
# from flite.users.permissions import IsUserOrReadOnly
from flite.users.serializers import CreateDepositSerializer


class DepositViewSet(mixins.CreateModelMixin,
                     viewsets.GenericViewSet):
    """
    Creates a deposit into a user account
    """
    queryset = Transaction.objects.all()
    serializer_class = CreateDepositSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.context["user_id"] = kwargs.get('user_id', None)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
