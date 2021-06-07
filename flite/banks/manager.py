from flite.banks.models import Bank


class AccountManager:
    @classmethod
    def get_bank(cls, **query_params):
        try:
            return AllBanks.objects.get(**query_params)
        except Bank.DoesNotExist:
            return None

    @classmethod
    def add_bank(cls, owner, bank, account_name, account_number, account_type):
        return Bank.objects.create(
            owner=owner,
            bank=bank,
            account_name=account_name,
            account_number=account_number,
            account_type=account_type,
        )

    @classmethod
    def all_accounts(cls, user):
        return Bank.objects.filter(user=user)
