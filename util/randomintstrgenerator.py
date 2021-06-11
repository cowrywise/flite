import random
import string


def generate_random_alphanum(lenght):
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in
                   range(lenght))
