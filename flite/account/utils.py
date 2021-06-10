import random
import re
import string

from rest_framework import serializers
from flite.account.models import Account, User, Bank, \
    Card


def randomStringDigits(stringLength=10):
    """Create and return random strings"""
    lettersAndDigits = 'FL' + string.ascii_letters + string.digits
    return ''.join(
        random.choice(lettersAndDigits) for i in range(stringLength))


def is_valid_uuid(value: str):
    """Validate a string is uuid"""

    # Regex to check valid
    # GUID (Globally Unique Identifier)
    regex = "^[{]?[0-9a-fA-F]{8}" + "-([0-9a-fA-F]{4}-)" + "{3}[0-9a-fA-F]{12}[}]?$"

    # Compile the ReGex
    p = re.compile(regex)

    # If the string is empty
    # return false
    if value is None:
        return False

    # Return if the string
    # matched the ReGex
    if (re.search(p, value)):
        return True
    else:
        return False


def get_valid_receipient(model, value: str) -> Account:
    if not is_valid_uuid(value):
        raise serializers.ValidationError(
            '''Please enter a valid receipient ID(uuid).''')
    receipient = Account.objects.filter(id=value).first()
    if not receipient:
        raise serializers.ValidationError(
            '''No Receipient with this account ID. Please add a valid receipient ID to proceed.'''
        )
    return receipient


def get_valid_bank(model, owner: User, value) -> Bank:
    """Get and return user bank

    Args:
        value: The id of the bank to be validated
        owner: The owner of the bank

    Returns:
        bank: Bank instance with 'value' ID

    Exceptions:
        ValidationError: This error is raised if an
            invalid bank ID was entered or bank does
            not belong to user instance
    """

    if not value.isdigit:
        raise serializers.ValidationError(
            '''Please enter a valid Bank ID(int).''')

    bank = model.objects.filter(owner=owner, id=value).first()
    if not bank:
        raise serializers.ValidationError(
            '''We care about the safety of your funds so we will only transfer to
    a verified bank you own. Please add a verified bank to proceed. .''')
    return bank


def get_valid_card(model, owner: User, value: str) -> Card:
    """Get and return user card

    Args:
        value: The id of the card to be validated
        owner: The owner of the card

    Returns:
        card: Card instance with 'value' ID

    Exceptions:
        ValidationError: This error is raised if an
            invalid card ID was entered or card does
            not belong to user instance
    """
    if not is_valid_uuid(value):
        raise serializers.ValidationError(
            '''Please enter a valid Card ID(uuid).''')
    card = model.objects.filter(owner=owner, id=value).first()
    if not card:
        raise serializers.ValidationError(
            '''You can only deposit funds from your card. Please add a verified card to proceed.'''
        )
    return card
