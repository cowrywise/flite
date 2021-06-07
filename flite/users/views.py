from django.db.models import query
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import User, NewUserPhoneVerification
from .permissions import IsOwner, IsOwnerOrReadOnly
from .serializers import CreateUserSerializer, UserSerializer, SendNewPhonenumberSerializer, P2PTransferSerializer, BankTransferSerializer, TransactionSerializer
# from rest_framework.views import APIView
from . import utils
from rest_framework.decorators import action, permission_classes
from rest_framework import status

class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """
    Updates and retrieves user accounts
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsOwnerOrReadOnly,)



class UserCreateViewSet(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    """
    Creates user accounts
    """
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = (AllowAny,)


class UserBankTransfersViewset(viewsets.GenericViewSet):
    """
    Creates deposits and withdrawals
    """

    serializer_class = BankTransferSerializer

    @action(methods=['post'], detail=True, permission_classes=[AllowAny])
    def deposits(self, request, pk=None):
        """
        view to create deposits
        """
        user = get_object_or_404(User, pk=pk)

        serializer = BankTransferSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(owner=user)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @action(methods=['post'], detail=True, permission_classes=[IsOwner])
    def withdrawals(self, request, pk=None):
        """
        view to create withdrawals
        """
        user = get_object_or_404(User, pk=pk)
        self.check_object_permissions(request, user)
        
        withdrawal_data = request.data.copy()

        try:
            amount = int(withdrawal_data.get('amount')) * -1
            withdrawal_data['amount'] = amount
            # negate amount so it's subtracted from user's available balance before saving the instance

        except ValueError:
            pass

        serializer = BankTransferSerializer(data=withdrawal_data)

        if serializer.is_valid():
            serializer.save(owner=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


class UserP2PTransferCreateViewSet(viewsets.GenericViewSet):
    """
    Create P2P transfers
    """
    serializer_class = P2PTransferSerializer

    
    @action(methods=['post'], detail=False, permission_classes=[IsOwner], 
            url_path='(?P<sender_id>[^/.]+)/transfers/(?P<recipient_id>[^/.]+)')
    def transfers(self, request, sender_id=None, recipient_id=None):
        """
        make transfers from one account to another
        """
        sender = get_object_or_404(User, pk=sender_id)
        recipient = get_object_or_404(User, pk=recipient_id)

        self.check_object_permissions(request, sender)
        if sender.pk == recipient.pk:
            # abort transfer if user is attempting to make a transfer to themselves
            error_response = {'detail': 'Cannot make a transfer to yourself'}
            
            return Response(error_response, status=status.HTTP_403_FORBIDDEN)

        serializer = P2PTransferSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sender=sender, recipient=recipient, owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserAccountTransactionsViewSet(viewsets.GenericViewSet):
    """
    Retrieve transaction lists and transaction details
    """
    serializer_class = TransactionSerializer
    

    @action(methods=['get'], detail=False, permission_classes=[IsOwner], url_path='(?P<pk>[^/.]+)/transactions')
    def transactions_list(self, request, pk=None):
        """
        retrieve transaction list
        """
        user = get_object_or_404(User, pk=pk)
        self.check_object_permissions(request, user)

        transations = user.transactions.all()
        serializer = TransactionSerializer(transations, many=True)


        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, permission_classes=[IsOwner], url_path='transactions/(?P<transaction_id>[^/.]+)')
    def transactions_detail(self, request, pk=None, transaction_id=None):
        """
        retrieve transaction details
        """
        user = get_object_or_404(User, pk=pk)
        self.check_object_permissions(request, user)

        transaction = user.transactions.filter(pk=transaction_id).first()

        if not transaction:
            error_response = {'detail': 'transaction not found'}
            return Response(error_response, status=status.HTTP_200_OK)
        
        serializer = TransactionSerializer(transaction)

        return Response(serializer.data, status=status.HTTP_200_OK)
