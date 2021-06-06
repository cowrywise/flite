from rest_framework import viewsets, permissions, pagination, response
from flite.core.utils import Response, transaction_type
from flite.users.permissions import IsUserOrReadOnly
from flite.users.models import *
from .serializers import *
import secrets
import uuid


class TransactionListPagination(pagination.PageNumberPagination):
    page_size = 5
    page_size_query_param = 'size'
    max_page_size = 20

    def get_paginated_response(self, data):
        context = {  
        'next': self.get_next_link(),
        'previous': self.get_previous_link(),
        'count': self.page.paginator.count,
        'results': data,             
        }
        return response.Response(context)


class DepositsViewSet(viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated, IsUserOrReadOnly,)
    serializer_class = BankTransferSerializer 
    pagination_class = TransactionListPagination

    def create(self, request, user_id):
        try:            
            serializer = BankTransferSerializer(data=request.data)
            
            if serializer.is_valid(raise_exception=True):              
                get_bank = serializer.validated_data.get('bank')
                amount = serializer.validated_data.get('amount')           

                if not Bank.objects.filter(bank__name=get_bank).exists():
                    return Response(None, {'message':'invalid bank name'})

                elif not User.objects.filter(id=uuid.UUID(user_id)).exists():
                    return Response(None, {'message':'account does not exist'})

                else:        
                    owner_account = User.objects.get(id=uuid.UUID(user_id))
                    get_bank = Bank.objects.get(bank__name=get_bank, owner=owner_account)
                    owner_bal = Balance.objects.get(owner=owner_account, active=True)
                    owner_bal.book_balance += float(amount)
                    owner_bal.available_balance += float(amount)
                    owner_bal.save()
                    reference_code = secrets.token_urlsafe(6)
                    serializer.save(
                    bank=get_bank,
                    owner=owner_account,
                    reference=reference_code,
                    status='succeessful',
                    amount=float(amount),
                    new_balance=owner_bal.available_balance,
                    transaction_type='banktransfer',
                    )
                    transaction = TransactionSerializer(
                        Transaction.objects.get(reference=reference_code),many=False).data  

                return Response({'transaction':transaction})

        except Exception as e:
            return Response(None, {'message':f'{e}'})
      

class WithdrawalsViewSet(viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated, IsUserOrReadOnly,)
    serializer_class = WithdrawalSerializer   
    
    def create(self, request, user_id):
        try:            
            serializer = WithdrawalSerializer(data=request.data)
           
            if serializer.is_valid(raise_exception=True):                
                get_owner= User.objects.get(id=uuid.UUID(user_id))                
                amount = serializer.validated_data.get('amount')          

                if not User.objects.filter(username=get_owner).exists():
                    return Response(None, {'message':'account does not exist'})                

                else:
                    owner_account = User.objects.get(username=get_owner)
                    owner_bal = Balance.objects.get(owner=owner_account, active=True)  
                    if float(amount) > owner_bal.available_balance:
                        return Response(None, {'message':'insufficient funds'})                  
                    owner_bal.book_balance -= float(amount)
                    owner_bal.available_balance -= float(amount)
                    owner_bal.save()
                    reference_code = secrets.token_urlsafe(6)
                    Transaction.objects.create(
                    owner=owner_account,
                    reference=reference_code,
                    status='succeessful',
                    amount=float(amount),
                    new_balance=owner_bal.available_balance,
                    transaction_type='withdrawal',
                    )
                    transaction = TransactionSerializer(
                        Transaction.objects.get(reference=reference_code),many=False).data  

                return Response({'transaction':transaction})

        except Exception as e:
            return Response(None, {'message':f'{e}'})
      

class P2PTransferViewSet(viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated, IsUserOrReadOnly,)
    serializer_class = WithdrawalSerializer 
    
    def create(self, request, sender_account_id, recipient_account_id):
        try:            
            serializer = WithdrawalSerializer(data=request.data)
            
            if serializer.is_valid(raise_exception=True):             
                get_amount = float(serializer.validated_data.get('amount'))          

                if not User.objects.filter(id=uuid.UUID(sender_account_id)).exists():
                    return Response(None, {'message':'account does not exist'})

                if not User.objects.filter(id=uuid.UUID(recipient_account_id)).exists():
                    return Response(None, {'message':'receipient account does not exist'})   

                sender_account = User.objects.get(id=uuid.UUID(sender_account_id))
                recipient_account = User.objects.get(id=uuid.UUID(recipient_account_id))
                # impliment debit and credit
                debit = Balance.objects.get(owner=sender_account, active=True)                    
                if get_amount > debit.available_balance:
                    return Response(None, {'message':'insufficent funds'})  

                if not Balance.objects.filter(owner=recipient_account, active=True).exists():
                    Balance.objects.create(owner=recipient_account, active=True)
                    
                credit = Balance.objects.get(owner=recipient_account, active=True)
                debit.book_balance -= float(get_amount)
                debit.available_balance -= float(get_amount)
                credit.book_balance += float(get_amount)
                credit.available_balance += float(get_amount)
                debit.save()
                credit.save()

                reference_code = secrets.token_urlsafe(6)
                P2PTransfer.objects.create(
                sender=sender_account,
                receipient=recipient_account,
                owner=sender_account,
                reference=reference_code,
                status='succeessful',
                amount=get_amount,
                new_balance=debit.available_balance,
                transaction_type='p2pTransfer',
                )
                p2pTransfer = P2PTransferSerializer(
                    P2PTransfer.objects.get(reference=reference_code),many=False).data  

                return Response({'p2pTransfer':p2pTransfer})

        except Exception as e:
            return Response(None, {'message':f'{e}'})


class TransactionListViewSet(viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated, IsUserOrReadOnly,)
    serializer_class = TransactionSerializer
    pagination_class = TransactionListPagination 
    queryset  = Transaction.objects.all()    
       
    def list(self, request, account_id):
        try:
            get_transaction = Transaction.objects.filter(owner__id=uuid.UUID(account_id)
                ) 
            page = self.paginate_queryset(get_transaction)            
            serializer = TransactionSerializer(page, many=True,context={'request': request})
            return self.get_paginated_response(serializer.data)

        except Exception as e:
            return Response(None,{'message':f'{e}'})


class RetrieveTransactionViewSet(viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated, IsUserOrReadOnly,)
    serializer_class = TransactionSerializer    
    queryset  = Transaction.objects.all()       
       
    def list(self, request, account_id, transaction_id):
        try:
            get_transaction = Transaction.objects.filter(
                id=uuid.UUID(transaction_id),
                owner__id=uuid.UUID(account_id)
                ) 
            page = self.paginate_queryset(get_transaction)            
            serializer = TransactionSerializer(page, many=True,context={'request': request})
            return self.get_paginated_response(serializer.data)

        except Exception as e:
            return Response(None,{'message':f'{e}'})
