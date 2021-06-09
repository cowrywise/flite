import uuid
from random import random
from string import digits

from django.db.models import F

from flite.users import models
from flite.users.models import Balance, Transaction


def generate_digits(length):
    code = ""
    for i in range(length):
        code += random.choice(digits)
    return code


def generate_new_user_passcode():
    """
    Returns a unique passcode
    """
    def _passcode():
        return str(uuid.uuid4().int)[0:6]
    passcode = _passcode()
    while models.NewUserPhoneVerification.objects.filter(referral_code=passcode).exists():
        passcode = _passcode()
    return passcode


def send_mobile_signup_sms(phone_number, email):

    status=False
    user_passcode = generate_new_user_passcode()
    
    try:
        attempted_verification_obj = models.NewUserPhoneVerification.objects.get(phone_number=phone_number)
    except models.NewUserPhoneVerification.DoesNotExist:
        attempted_verification_obj = None

    if attempted_verification_obj:
        attempted_verification_obj.verification_code = user_passcode
        attempted_verification_obj.email = email
        attempted_verification_obj.is_verified = False
        attempted_verification_obj.save()
    else:
        attempted_verification_obj = models.NewUserPhoneVerification(phone_number=str(phone_number), verification_code=user_passcode,
            is_verified=False, email=email)
        attempted_verification_obj.save()    
    #tasks.send_sms_verification_code.delay(phone_number, user_passcode)
    status = True
    return attempted_verification_obj, user_passcode


def validate_mobile_signup_sms(phone_number, code):

    try:
        new_user_code_obj  = models.NewUserPhoneVerification.objects.get(phone_number=phone_number, verification_code=code)
    except models.NewUserPhoneVerification.DoesNotExist:
        new_user_code_obj = None

    if new_user_code_obj:
        if new_user_code_obj.is_verified:
            return 0, "Code has been verified"
        else:
            new_user_code_obj.is_verified = True
            new_user_code_obj.save()
            return 1, "Code verified"
    return 0, "The code provided is invalid. Kindly check and try again."


def perform_credit_transaction(owner, amount, refrence):
    balance = Balance.objects.get(owner=owner)
    balance.available_balance = F('available_balance') + amount
    balance.refresh_from_db()

    """ create a log """
    transaction = Transaction.objects.create(owner=owner, reference=refrence, status="Approved",
                                             amount=amount, new_balance=balance.available_balance)


def deposit_transaction(user, amount):
    perform_credit_transaction(user, amount, f"Deposit made with ID: {generate_digits(10)}")