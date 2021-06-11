from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from .views import get_balance, fund_account, withdraw_funds, AllAccountTransactions, ViewAccountTransaction, \
    transfer_funds,  BankList, CreateBankAccountView

app_name = 'users'


urlpatterns = [
    path('api/v1/user/balance/<str:user_id>/', get_balance, name='get_balance'),
    path('api/v1/user/<str:user_id>/deposits/', fund_account, name='fund_account'),
    path('api/v1/user/<str:user_id>/withdrawals/', withdraw_funds, name='withdraw_funds'),
    path('api/v1/account/<str:balance_id>/transactions/<str:transaction_id>/', ViewAccountTransaction.as_view(),
         name='view_account_transaction'),
    path('api/v1/account/<str:balance_id>/transaction/', AllAccountTransactions.as_view(),
         name='all_accounts_transaction'),
    path('api/v1/account/<str:sender_balance_id>/transfer/<str:receiver_balance_id>/', transfer_funds, name='transfer'),
    path('api/v1/banks/', BankList.as_view(), name='all_banks'),
    path('api/v1/bank/', CreateBankAccountView.as_view(), name='create_bank'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

