import json 
import random
import string


def randomStringDigits(stringLength=10):
    lettersAndDigits = 'FL' + string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))