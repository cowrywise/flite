from rest_framework import viewsets, mixins
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User, NewUserPhoneVerification, Balance, P2PTransfer, Transaction
from .permissions import IsUserOrReadOnly
from .serializers import CreateUserSerializer, UserSerializer, SendNewPhonenumberSerializer, BalanceSerializer, TransactionSerializer
from rest_framework.views import APIView
from . import utils
from rest_framework import status


class UsersListView(APIView):
    """
    This resource gets the details of a given account
    """

    permission_classes = (AllowAny,)
    
    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        users = User.objects.all()
        page = request.query_params.get('page')
        limit = request.query_params.get('limit')
        if page:
            paginator = Paginator(users, 5)
            if limit:  # If limit is specified, use it for pagination
                paginator = Paginator(users, int(limit))
            try:
                paginated_users = paginator.page(page)
            except EmptyPage:
                paginated_users = []
            serializer = UserSerializer(paginated_users, many=True)
            return Response({"page": page, "data": serializer.data}, status=status.HTTP_200_OK)
        serializer = UserSerializer(users[:5], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, format=None):
        """
        Create a new user.
        {
            "username": "second",
            "password": "hello123",
            "email": "second@delight.com"
        }
        """
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    

    

class P2PTransferView(APIView):

    permission_classes = (AllowAny,)

    def generate_transaction_reference(self):
        """
        Generate Transaction reference
        """
        import random, string
        reference = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
        return reference

    def post(self, request, sender_account_id, recipient_account_id, format=None):
        """
        Transfer money from one user to another
        """

        amount = request.data.get('amount')
        if sender_account_id is None or recipient_account_id is None or amount is None:
            return Response({"error": "Sender, receiver or amount not provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = float(amount)
        except ValueError:
            return Response({"error": "Invalid amount provided."}, status=status.HTTP_400_BAD_REQUEST)

        sender_balance = get_object_or_404(Balance, owner__id=sender_account_id)
        receiver_balance = get_object_or_404(Balance, owner__id=recipient_account_id)

        # Assume that the sender has sufficient balance

        receiver_balance.available_balance += amount
        receiver_balance.book_balance += amount

        receiver_balance.save()

        reference = self.generate_transaction_reference()

        P2PTransfer.objects.create(
            owner=get_object_or_404(User, pk=sender_account_id),
            sender=get_object_or_404(User, pk=sender_account_id),
            receipient=get_object_or_404(User, pk=recipient_account_id),
            reference=reference,
            status='SUCCESS',
            amount=amount,
            new_balance=sender_balance.available_balance
        )

        return Response({"message": "Transfer successful.", "amount":amount, "receiver_balance": receiver_balance.available_balance, "sender_balance": sender_balance.available_balance, "reference": reference}, status=status.HTTP_200_OK)
    

class TransactionsListView(APIView):

    permission_classes = (IsUserOrReadOnly,)

    def get(self, request, account_id):
        transactions = Transaction.objects.filter(owner__id=account_id).order_by('id')
        page = request.query_params.get('page')
        if page:
            paginator = Paginator(transactions, 5)
            try:
                paginated_transactions = paginator.page(page)
            except EmptyPage:
                paginated_transactions = []
            serializer = TransactionSerializer(paginated_transactions, many=True)
            return Response({"page": page, "data": serializer.data}, status=status.HTTP_200_OK)
        serializer = TransactionSerializer(transactions[:5], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TransactionDetailView(APIView):

    permission_classes = (IsUserOrReadOnly,)

    def get(self, request, account_id, transaction_id):
        transaction = get_object_or_404(Transaction, owner=account_id, reference=transaction_id)
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data)


class UserDetailView(APIView):
    """
    This resource gets the details of a given account
    """
        
    def get(self, request, user_id, format=None):
        """
        Return a list of all users.
        """
        user = get_object_or_404(User, pk=user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    def put(self, request, user_id, format=None):
        """
        Update a user instance.
        """
        user = get_object_or_404(User, id=user_id)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class UserDepositView(APIView):
    """
    A view for updating deposits related to a specific user's balance.
    """

    permission_classes = (AllowAny,)  # Assuming you want only authenticated users to access this endpoint

    def generate_transaction_reference(self):
        """
        Generate Transaction reference
        """
        import random, string
        reference = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
        return reference

    def create_transaction(self, user_id, amount, new_balance):
        Transaction.objects.create(
            owner=get_object_or_404(User, pk=user_id),
            reference=self.generate_transaction_reference(),
            status='SUCCESS',
            amount=amount,
            new_balance=new_balance
        )

    def update_balance(self, user_id, amount):
        balance = get_object_or_404(Balance, owner__id=user_id)
        balance.available_balance += amount
        balance.book_balance += amount
        balance.save()
        return balance

    def post(self, request, user_id=None):
        """
        Update a deposit related to the specified user's balance.
        """

        
        amount = request.data.get('amount')
        if amount is None:
            return Response({"error": "Amount not provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = float(amount)
        except ValueError:
            return Response({"error": "Invalid amount provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Update available_balance field
        balance = self.update_balance(user_id, amount)
        # Create transaction record
        self.create_transaction(user_id, amount, balance.available_balance)

        serializer = BalanceSerializer(balance)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class UserWithdrawalView(APIView):
    """
    A view for updating deposits related to a specific user's balance.
    """

    permission_classes = (AllowAny,)  # Assuming you want only authenticated users to access this endpoint

    def generate_transaction_reference(self):
        """
        Generate Transaction reference
        """
        import random, string
        reference = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
        return reference

    def create_transaction(self, user_id, amount, new_balance):
        Transaction.objects.create(
            owner=get_object_or_404(User, pk=user_id),
            reference=self.generate_transaction_reference(),
            status='SUCCESS',
            amount=amount,
            new_balance=new_balance
        )

    def update_balance(self, user_id, amount):
        balance = get_object_or_404(Balance, owner__id=user_id)
        balance.available_balance -= amount
        balance.book_balance -= amount
        balance.save()
        return balance

    def post(self, request, user_id=None):
        """
        Update a deposit related to the specified user's balance.
        """

        
        amount = request.data.get('amount')
        if amount is None:
            return Response({"error": "Amount not provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = float(amount)
        except ValueError:
            return Response({"error": "Invalid amount provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Update available_balance field
        balance = self.update_balance(user_id, amount)
        # Create transaction record
        self.create_transaction(user_id, amount, balance.available_balance)

        serializer = BalanceSerializer(balance)
        return Response(serializer.data, status=status.HTTP_200_OK)



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
