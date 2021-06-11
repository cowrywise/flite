from rest_framework import viewsets, mixins
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import User, NewUserPhoneVerification, Transaction
from .permissions import IsUserOrReadOnly
from .serializers import CreateUserSerializer, UserSerializer, SendNewPhonenumberSerializer, DepositSerializer, \
    UserTransactionListSerializer
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from . import utils
from .utils import deposit_transaction, withdraw_transaction, transfer_transaction


class UserViewSet(ListAPIView):
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


class SendNewPhonenumberVerifyViewSet(mixins.CreateModelMixin,mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    Sending of verification code
    """
    queryset = NewUserPhoneVerification.objects.all()
    serializer_class = SendNewPhonenumberSerializer
    permission_classes = (AllowAny,)


    def update(self, request, pk=None,**kwargs):
        verification_object = self.get_object()
        code = request.data.get("code")

        if code is None:
            return Response({"message":"Request not successful"}, 400)    

        if verification_object.verification_code != code:
            return Response({"message":"Verification code is incorrect"}, 400)    

        code_status, msg = utils.validate_mobile_signup_sms(verification_object.phone_number, code)
        
        content = {
                'verification_code_status': str(code_status),
                'message': msg,
        }
        return Response(content, 200)


class UserList(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsUserOrReadOnly, ]

    def dispatch(self, request, *args, **kwargs):
        try:
            self.user_id = kwargs.pop('user_id')
        except KeyError:
            self.user_id = None
        return super().dispatch(request, *args, **kwargs)

    def list(self, request):
        if self.user_id:
            queryset = self.queryset.filter(id=self.user_id)
        else:
            queryset = self.get_queryset()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def deposit_account(request, user_id):
    #{"amount":  2000}
    data = request.data
    serializer = DepositSerializer(data=data)
    if serializer.is_valid():
        amount = serializer.validated_data.get('amount')
        user = User.objects.filter(id=user_id).first()
        if user:
            deposit_transaction(user, amount)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class DepositAccountView(APIView):
    def dispatch(self, request, *args, **kwargs):
        """Updates the keyword args to always have 'foo' with the value 'bar'"""
        kwargs.update({'foo': 'bar'})  # inject the foo value
        # now process dispatch as it otherwise normally would
        return super().dispatch(request, *args, **kwargs)

    def post(self):
        pass


@api_view(['POST'])
def withdraw_account(request, user_id):
    data = request.data
    serializer = DepositSerializer(data=data)
    if serializer.is_valid():
        amount = serializer.validated_data.get('amount')
        user = User.objects.filter(id=user_id).first()
        if user:
            if withdraw_transaction(user, amount):
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"message": "insufficient fund "}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "User not found"}, status=status.HTTP_400_OK)
    else:
        return Response({"error": serializer.errors}, status=status.HTTP_400_OK)


@api_view(['POST'])
def transfer(request, sender_account_id, recipient_account_id):
    data = request.data
    serializer = DepositSerializer(data=data)
    if serializer.is_valid():
        amount = serializer.validated_data.get('amount')
        sender = User.objects.filter(id=sender_account_id).first()
        receiver = User.objects.filter(id=recipient_account_id).first()

        if sender and receiver:
            if transfer_transaction(sender, receiver, amount):
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"message": "insufficient fund for sender "}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "User not found"}, status=status.HTTP_400_OK)
    else:
        return Response({"error": serializer.errors}, status=status.HTTP_400_OK)


class AccountTransactionListView(ListAPIView):
    """
    Get all the list settlement account under the current tenant user
    Method `GET`<br>
    Format `Json` <br>
    Authorization: Token based auth is required

    Response:
        <pre>


        </pre>
    """
    serializer_class = UserTransactionListSerializer
    # pagination_class = LargeResultsSetPagination
    permission_classes = (IsUserOrReadOnly,)

    def get_queryset(self):
        owner = self.owner
        data = Transaction.objects.filter(owner=owner)

        return data

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
                "message": "User Transaction List",
                "responseCode": "100",
                'count': queryset.count(),
                'next': None,
                'previous': None,
                "data": serializer.data
            }, status=status.HTTP_200_OK)


class AccountTransactionListView(ListAPIView):
    """
    Get all the list settlement account under the current tenant user
    Method `GET`<br>
    Format `Json` <br>
    Authorization: Token based auth is required

    Response:
        <pre>


        </pre>
    """
    serializer_class = UserTransactionListSerializer
    # pagination_class = LargeResultsSetPagination
    permission_classes = (IsUserOrReadOnly,)

    def get_queryset(self):
        owner = self.owner
        id = self.id
        data = Transaction.objects.filter(owner=owner, id=id)

        return data

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
                "message": "User Transaction List",
                "responseCode": "100",
                'count': queryset.count(),
                'next': None,
                'previous': None,
                "data": serializer.data
            }, status=status.HTTP_200_OK)
