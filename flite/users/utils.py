import uuid
from flite.users import models
from django.db.models import F
import time

# constants
CREDIT='CREDIT'
DEBIT='DEBIT'

PENDING='PENDING'
DECLINED='DECLINED'
COMPLETED='COMPLETED'


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


def generate_transaction_refrence_code():
    """
    Returns a unique transaction reference 
    """
    def _transaction_ref():
        now = time.time()
        return 'TRAN-REF-' + str(now).replace('.','')
    transaction_ref = _transaction_ref()
    while models.Transaction.objects.filter(reference=transaction_ref).exists():
        transaction_ref = _transaction_ref()
    return transaction_ref


def log_transaction(**kwargs):
    transaction = models.Transaction(
        owner=kwargs['user'],
        reference=kwargs['reference'],
        status=kwargs['status'],
        type=kwargs['type'],
        amount=kwargs['amount'],
        new_balance=kwargs['new_balance']
    )

    transaction.save()

    return transaction


def check_balance(user):
    b = models.Balance.objects.get(owner=user)
    return b.available_balance


def p2p_transfer(sender, recipient, amount):
    """
    Utility used in P2PTransferView
    :sender  & :recipient are balance objects and not user's
    :return (Boolean, Message)
    """
    sender_balance = sender.available_balance

    # prevent transfers
    if sender.id == recipient.id:
        return False, 'You can not transfer to the same account'

    if sender_balance < amount or sender_balance == 0:
        return False, 'Insufficient funds'

    # debit sender's account
    sender.available_balance = F('available_balance') - amount
    sender.book_balance = F('book_balance') - amount

    # credit recipient's account 
    recipient.available_balance = F('available_balance') + amount
    recipient.book_balance = F('book_balance') + amount

    # commit 
    sender.save()
    recipient.save()

    # refresh
    sender.refresh_from_db()
    recipient.refresh_from_db()

    # log transactions 

    # sender (debit)
    log_transaction(
        user=sender.owner,
        reference=generate_transaction_refrence_code(),
        status=COMPLETED,
        type=DEBIT,
        amount=amount,
        new_balance=sender.available_balance
    )

    # recipient (credit)
    log_transaction(
        user=recipient.owner,
        reference=generate_transaction_refrence_code(),
        status=COMPLETED,
        type=CREDIT,
        amount=amount,
        new_balance=recipient.available_balance
    )


    return True, 'Transfer successful'
