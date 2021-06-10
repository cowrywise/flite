import factory
from django.utils.crypto import get_random_string
import datetime
from faker import Factory
from ..models import STATUS_TYPE, TRANSFER_TYPE, TRANSACTION_TYPE

faker = Factory.create()


class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'users.User'
        django_get_or_create = ('username',)

    id = factory.Faker('uuid4')
    username = factory.Sequence(lambda n: f'testuser{n}')
    password = factory.Faker('password', length=10, special_chars=True, digits=True,
                             upper_case=True, lower_case=True)
    email = factory.Faker('email')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True
    is_staff = False


STATUS = [x[0] for x in STATUS_TYPE]


class FundFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'users.Fund'

    receiver = factory.SubFactory(UserFactory)
    amount = faker.random_number()
    reference = get_random_string()
    status = factory.fuzzy.FuzzyChoice(STATUS)


TYPE = [x[0] for x in TRANSFER_TYPE]


class TransferFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'users.Transfer'

    receiver = factory.SubFactory(UserFactory)
    sender = factory.SubFactory(UserFactory)
    amount = faker.random_number()
    reference = get_random_string()
    status = factory.fuzzy.FuzzyChoice(STATUS)
    transfer_type = factory.fuzzy.FuzzyChoice(TYPE)


class WithdrawFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'users.Withdraw'

    receiver = factory.SubFactory(UserFactory)
    amount = faker.random_number()
    reference = get_random_string()
    status = factory.fuzzy.FuzzyChoice(STATUS)


class BalanceFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'users.Balance'

    owner = factory.SubFactory(UserFactory)
    available_balance = faker.random_number()
    reference = get_random_string()
    active = True


TRANSACTION = [x[0] for x in TRANSACTION_TYPE]


class TransactionFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'users.Transaction'

    owner = factory.SubFactory(UserFactory)
    balance = factory.SubFactory(BalanceFactory)
    amount = faker.random_number()
    reference = get_random_string()
    status = factory.fuzzy.FuzzyChoice(STATUS)
    transfer_type = factory.fuzzy.FuzzyChoice(TRANSACTION)
