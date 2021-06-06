import uuid
from flite.users import models

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

def generate_transaction_referencecode():
    """
    Returns a unique reference code for transaction
    """
    def _reference_code():
        return "TRANS-" + str(uuid.uuid4().int)[0:10]
    code = _reference_code()
    while models.Transaction.objects.filter(reference=code).exists():
        code = _reference_code()
    return code

