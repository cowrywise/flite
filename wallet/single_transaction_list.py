from rest_framework.response import Response

from flite.users.models import User, Transaction
from util.mandatory_field_checker import check_empty_string
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def list_single_transactions_by_reference(request, account_id=None, transaction_id=None):
    try:
        # TODO: Assumptions
        # TODO: Verify JWT token
        # TODO: Verify username in token matches draccount name

        check_if_empty = {"account_id": account_id
                          }
        check_empty_string_result = check_empty_string(check_if_empty)
        if check_empty_string_result != True:
            return Response({
                "responseCode": "19",
                "responseMessage": "the following fields %s can't be empty" % str(check_empty_string_result).replace(
                    "'",
                    "").replace(
                    "[", "").replace("]", ""),
                "data": []
            })

        user_instance = User.objects.get(id=account_id)
        list_transaction = Transaction.objects.filter(owner=user_instance, reference=transaction_id)[0]
        data = []
        if list_transaction:
            data.append(
                {
                    "owner": str(list_transaction.owner),
                    "reference": list_transaction.reference,
                    "status": list_transaction.status,
                    "amount": list_transaction.amount,
                    "new_balance": list_transaction.new_balance
                }
            )
            return Response({
                "responseCode": "200",
                "responseMessage": "transaction listing successful",
                "data": data
            })
        else:
            return Response({
                "responseCode": "404",
                "responseMessage": "transaction not found",
                "data": data
            })


    except Exception as e:
        print('Error at list_transactions_by_account_id: ', str(e))
        return Response({
            "responseCode": "409",
            "responseMessage": "something went wrong",
            "data": []
        })
