import json 
import random
import string
import re

from rest_framework import serializers



def randomStringDigits(stringLength=10):
    lettersAndDigits = 'FL' + string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))


def is_valid_uuid(str):
 
    # Regex to check valid
    # GUID (Globally Unique Identifier)
    regex = "^[{]?[0-9a-fA-F]{8}" + "-([0-9a-fA-F]{4}-)" + "{3}[0-9a-fA-F]{12}[}]?$"
         
    # Compile the ReGex
    p = re.compile(regex)
 
    # If the string is empty
    # return false
    if (str == None):
        return False
 
    # Return if the string
    # matched the ReGex
    if(re.search(p, str)):
        return True
    else:
        return False


def get_valid_bank(model, owner, value):
    if not value.isdigit:
        raise serializers.ValidationError(
    '''Please enter a valid Bank ID(int).''')

    bank = model.objects.filter(owner=owner, id=value).first()
    if not bank:
        raise serializers.ValidationError(
    '''We care about the safety of your funds so we will only transfer to
    a verified bank you own. Please add a verified bank to proceed. .''')
    return bank


def get_valid_card(model, owner, value):
    if not is_valid_uuid(value):
        raise serializers.ValidationError(
    '''Please enter a valid Card ID(uuid).''')
    card = model.objects.filter(owner=owner, id=value).first()
    if not card:
        raise serializers.ValidationError(
    '''You can only deposit funds from your card. Please add a verified card to proceed.''')
    return card
