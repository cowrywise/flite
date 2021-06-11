from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import *
from .permissions import IsUserOrReadOnly
from .serializers import *
from rest_framework.views import APIView
from . import utils
from rest_framework import status

class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """
    Updates and retrieves user accounts
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsUserOrReadOnly,)


class UserCreateViewSet(mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    """
    Creates user accounts
    """
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = (AllowAny,)


class SendNewPhonenumberVerifyViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    Sending of verification code
    """
    queryset = NewUserPhoneVerification.objects.all()
    serializer_class = SendNewPhonenumberSerializer
    permission_classes = (AllowAny,)

    def update(self, request, pk=None, **kwargs):
        verification_object = self.get_object()
        code = request.data.get("code")

        if code is None:
            return Response({"message": "Request not successful"}, 400)

        if verification_object.verification_code != code:
            return Response({"message": "Verification code is incorrect"}, 400)

        code_status, msg = utils.validate_mobile_signup_sms(verification_object.phone_number, code)

        content = {
            'verification_code_status': str(code_status),
            'message': msg,
        }
        return Response(content, 200)

class DepositViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    Deposit money to a user
    """
    queryset = Transaction.objects.all()
    serializer_class = DepositSerializer
    permission_classes = (AllowAny,)
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        createdInstance = serializer.save()
        deposit_serializer = DepositSerializer(createdInstance)
        headers = self.get_success_headers(deposit_serializer.data)
        return Response(
            deposit_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

class WithdrawalViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    Deposit money to a user
    """
    queryset = Transaction.objects.all()
    serializer_class = WithdrawalSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        createdInstance = serializer.save()
        withdrawal_serializer = WithdrawalSerializer(createdInstance)
        headers = self.get_success_headers(withdrawal_serializer.data)
        return Response(
            withdrawal_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )
