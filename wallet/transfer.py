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
def transfer_cash(request, sender_account_id=None, recipient_account_id=None):
    try:
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
        beneusername = request.data.get("beneusername")
        draccountno = request.data.get("draccountno")
        craccountno = request.data.get("craccountno")
        narration = request.data.get("narration")
        pin = request.data.get("pin")
        requestReference = request.data.get("requestId")
        compulsory_fields = ['amount', 'username', 'beneusername', 'draccountno', 'requestId', 'narration', 'pin',
                             'craccountno']

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
                          "benefname": beneusername,
                          "draccountno": draccountno,
                          "narration": narration,
                          "amount": amount,
                          "requestReference": requestReference,
                          "pin": pin,
                          "craccountno": craccountno
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

        # Check draccountno is valid
        # Assumption: A user can have only one account
        print(username)
        print(beneusername)
        draccountno_user_instance = User.objects.get(username=username)
        craccountno_user_instance = User.objects.get(username=beneusername)
        dr_balance_object = Balance.objects.get(owner=draccountno_user_instance)
        print("blance retirieved")
        # Confirm draccountno is valid
        if dr_balance_object:
            # confirm draccountno is active
            if dr_balance_object.active:
                # confirm draccountno has sufficient funds
                if Decimal(amount) < Decimal(dr_balance_object.available_balance):
                    # Debit draccount
                    dr_balance_object_response = Balance.objects.filter(owner=draccountno_user_instance).update(
                        available_balance=F("available_balance") - Decimal(amount))
                    if dr_balance_object_response:
                        # For performance Spin background thread
                        # Payload for background thread
                        dict_payload = {
                            "owner": draccountno_user_instance,
                            "reference": requestReference,
                            "status": "debit successful",
                            "amount": amount,
                            "type": "debit"
                        }
                        # Spin thread to save latest
                        Thread(target=t_transaction_saver, kwargs=dict_payload).start()

                        # Assumption: name enquiry done on craccount
                        cr_balance_object_response = Balance.objects.filter(
                            owner=craccountno_user_instance).update(
                            available_balance=F("available_balance") + Decimal(amount))
                        if cr_balance_object_response:
                            dict_payload = {
                                "owner": craccountno_user_instance,
                                "reference": requestReference,
                                "status": "credit successful",
                                "amount": amount,
                                "type": "credit"
                            }
                            # Spin thread to save latest
                            Thread(target=t_transaction_saver, kwargs=dict_payload).start()
                            return Response({
                                "responseCode": "200",
                                "responseMessage": "₦%d successfully sent to %s" % (Decimal(amount), craccountno),
                                "data": ""
                            })
                        # Call reversal function
                        return Response({
                            "responseCode": "17",
                            "responseMessage": "something went wrong",
                            "data": ""
                        })

                    else:
                        return Response({
                            "responseCode": "17",
                            "responseMessage": "something went wrong",
                            "data": ""
                        })
                else:
                    return Response({
                        "responseCode": "17",
                        "responseMessage": "you do not have sufficient funds to carry out this transaction",
                        "data": ""
                    })
            else:
                return Response({
                    "responseCode": "17",
                    "responseMessage": "account on PND",
                    "data": ""
                })
        else:
            return Response({
                "responseCode": "17",
                "responseMessage": "invalid account number",
                "data": ""
            })
        if Decimal(amount) < 1:
            return Response({
                "responseCode": "17",
                "responseMessage": "invalid amount",
                "data": ""
            })

        return Response({
            "responseCode": "200",
            "responseMessage": "₦%d successfully withdrawn by %s" % (Decimal(amount), sender_account_id),
            "data": ""
        })
    except Exception as e:
        print('Error at transfer_cash: ', str(e))
        if "User matching query does not exist" in str(e):
            return Response({
                "responseCode": "409",
                "responseMessage": "invalid username or beneusername",
                "data": []
            })
        return Response({
            "responseCode": "409",
            "responseMessage": "something went wrong",
            "data": []
        })
