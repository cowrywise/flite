from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import *
from .permissions import IsUserOrReadOnly
from .serializers import *
from rest_framework.views import APIView
from . import utils
from rest_framework import status
from rest_framework.decorators import api_view

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

@api_view(['GET'])
def all_transactions(request, account_id):
    possibleUserAccount = Bank.objects.get(id=account_id)
    if not possibleUserAccount:
        responseDetails = utils.error_response('account does not exist')
        return Response(responseDetails, status=status.HTTP_404_NOT_FOUND)

    if possibleUserAccount.owner != request.user:
        responseDetails = utils.error_response('user not permitted to perform this operation')
        return Response(responseDetails, status=status.HTTP_403_FORBIDDEN)

    userTransactions = Transaction.objects.filter(owner=request.user)
    finalResponseData = utils.success_response('user transactions retrieved successfully', userTransactions)
    return Response(finalResponseData, status.HTTP_200_OK)

@api_view(['GET'])
def transaction_detail(request, account_id, transaction_id):
    possibleUserAccount = Bank.objects.get(id=account_id)
    if not possibleUserAccount:
        responseDetails = utils.error_response('account does not exist')
        return Response(responseDetails, status=status.HTTP_404_NOT_FOUND)

    if possibleUserAccount.owner != request.user:
        responseDetails = utils.error_response('user not permitted to perform this operation')
        return Response(responseDetails, status=status.HTTP_403_FORBIDDEN)

    singleUserTransaction = Transaction.objects.get(id=transaction_id)
    finalResponseData = utils.success_response(
        'user transaction retrieved successfully', singleUserTransaction)
    return Response(finalResponseData, status.HTTP_200_OK)

# @api_view(['POST'])
# def p2p_transfer(request, sender_account_id, recipient_account_id):

