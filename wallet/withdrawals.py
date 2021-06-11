from decimal import Decimal
from threading import Thread

from rest_framework.response import Response

from flite.users.models import User, Balance
from util.mandatory_field_checker import check_request_payload, check_empty_string
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from django.db.models import F

from util.threaded_transaction_saver import t_transaction_saver


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def withdrawal_cash(request, id=None):
    try:
        # TODO: Assumptions
        # TODO: Verify JWT token
        # TODO: Verify username in token matches draccount name
        # TODO: Verify Device macthes any known device
        # TODO: Name enquiry for craccountno is successful
        # TODO: Verify requestid is unique by saving, cancel transaction if not
        # TODO: Verify token
        # TODO: Verify draccount has no PND
        # TODO: Verify transactions falls withing draccount limit
        amount = request.data.get("amount")
        username = request.data.get("username")
        benefname = request.data.get("benefname")
        draccountno = request.data.get("draccountno")
        narration = request.data.get("narration")
        pin = request.data.get("pin")
        requestReference = request.data.get("requestId")
        compulsory_fields = ['amount', 'username', 'benefname', 'draccountno', 'requestId', 'narration', 'pin']

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
        check_if_empty = {"username": username,
                          "benefname": benefname,
                          "draccountno": draccountno,
                          "narration": narration,
                          "amount": amount,
                          "requestReference": requestReference,
                          "pin": pin
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
        if Decimal(amount) < 1:
            return Response({
                "responseCode": "17",
                "responseMessage": "invalid amount",
                "data": ""
            })
        draccountno_user_instance = User.objects.get(username=username)
        dr_balance_object = Balance.objects.get(owner=draccountno_user_instance)
        # confirm user has sufficient funds
        if Decimal(amount) < Decimal(dr_balance_object.available_balance):
            # Debit Account
            print("debiting")
            dr_balance_object_response = Balance.objects.filter(
                owner=draccountno_user_instance).update(
                available_balance=F("available_balance") - Decimal(amount))
            print("debiting done")
            # print(dr_balance_object_response)
            if dr_balance_object_response:
                dict_payload = {
                    "owner": draccountno_user_instance,
                    "reference": requestReference,
                    "status": "withdrawal successful",
                    "amount": amount,
                    "type": "debit"
                }
                # Spin thread to save latest
                Thread(target=t_transaction_saver, kwargs=dict_payload).start()
                return Response({
                    "responseCode": "200",
                    "responseMessage": "₦%d successfully withdrawn by %s" % (Decimal(amount), id),
                    "data": ""
                })
            else:
                return Response({
                    "responseCode": "300",
                    "responseMessage": "something went wrong",
                    "data": ""
                })
        else:
            return Response({
                "responseCode": "17",
                "responseMessage": "you do not have sufficient funds to carry out this transaction",
                "data": ""
            })
    except Exception as e:
        print('Error at withdrawal_cash: ', str(e))
        return Response({
            "responseCode": "409",
            "responseMessage": "something went wrong",
            "data": []
        })
