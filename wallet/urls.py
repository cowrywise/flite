from django.urls import path

from wallet.deposit import deposit_cash
from wallet.single_transaction_list import list_single_transactions_by_reference
from wallet.transaction_list import list_transactions_by_account_id
from wallet.transfer import transfer_cash
from wallet.withdrawals import withdrawal_cash

urlpatterns = [
    path('<str:id>/withdrawals', withdrawal_cash, name='withdrawals'),
    path('<str:id>/deposits', deposit_cash, name='deposits'),
    path('<str:sender_account_id>/transfers/<str:recipient_account_id>', transfer_cash, name='transfers'),
    path('<str:account_id>/transactions', list_transactions_by_account_id, name='transactions'),
    path('<str:account_id>/transactions/<str:transaction_id>', list_single_transactions_by_reference, name='transactions'),

]
