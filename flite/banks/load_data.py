import json
from flite.users.models import *


def add_banks():
    with open("flite/users/bank.json") as f:
        data = json.load(f)
        banks = data.get("data", {})
        for bank in banks:
            AllBanks.objects.create(name=bank["name"], bank_code=bank["code"])


