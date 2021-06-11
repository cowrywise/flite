from decimal import Decimal

from rest_framework.response import Response

from flite.users.models import User, Balance, Transaction
from util.mandatory_field_checker import check_request_payload, check_empty_string
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from django.db.models import F
from django.core.paginator import EmptyPage, Paginator, PageNotAnInteger


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def list_transactions_by_account_id(request, account_id=None):
    try:
        # TODO: Assumptions
        # TODO: Verify JWT token
        # TODO: Verify username in token matches draccount name

        num_of_page = request.data.get('pageNum')
        pagesize = request.data.get('pageSize')
        compulsory_fields = ['pageNum', 'pageSize']

        is_request_complete = check_request_payload(request.data, compulsory_fields)
        # Note: Do not simplify expression as suggested by IDE, eg: if not is_request_complete
        if is_request_complete != True:
            return Response({
                "responseCode": "401",
                "responseMessage": "compulsory request field missing: %s" % str(is_request_complete).replace("'",
                                                                                                             "").replace(
                    "{", "").replace("}", ""),
                "data": []
            })
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
        list_transaction = Transaction.objects.filter(owner=user_instance).order_by('-id')
        data = []
        paginator = Paginator(list_transaction, int(pagesize))
        try:
            list_profile = paginator.page(int(num_of_page))
            for obj in list_profile:
                data.append(
                    {
                        "owner": str(obj.owner),
                        "reference": obj.reference,
                        "status": obj.status,
                        "amount": obj.amount,
                        "new_balance": obj.new_balance
                    }
                )
        except PageNotAnInteger:
            list_profile = paginator.page(1)
            for obj in list_profile:
                data.append(
                    {
                        "owner": str(obj.owner),
                        "reference": obj,
                        "status": obj.status,
                        "amount": obj.amount,
                        "new_balance": obj.new_balance

                    }
                )
        except EmptyPage:
            data.append(
                {
                    "owner": "",
                    "reference": "",
                    "status": "",
                    "amount": "",
                    "new_balance": ""
                }
            )
        return Response({
            "responseCode": "200",
            "responseMessage": "Transaction listing successful",
            "data": data
        })

    except Exception as e:
        print('Error at list_transactions_by_account_id: ', str(e))
        return Response({
            "responseCode": "409",
            "responseMessage": "something went wrong",
            "data": []
        })
