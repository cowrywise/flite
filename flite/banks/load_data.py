import json
from flite.banks.models import AllBanks


def add_banks():
    with open("flite/banks/bank.json") as f:
        data = json.load(f)
        banks = data.get("data", {})
        for bank in banks:
            AllBanks.objects.create(name=bank["name"].lower(), bank_code=bank["code"])
