import factory
from ...users.models import Bank, AllBanks, P2PTransfer, BankTransfer, Transaction
import string

reference_words = [
    "Birthday Gift",
    "Surpise",
    "Vex Money",
    "School Fees",
    "Shopping"
]

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

class AllBanksFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = AllBanks
    
    id = factory.Faker('uuid4')
    name = factory.Faker('company')
    acronym = factory.Faker('bothify', text='???', letters=string.ascii_uppercase)
    bank_code = factory.Faker('numerify', text="##")

class BankFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Bank

    account_number = factory.Faker('numerify', text='#'*10)
    account_type = factory.Faker('word', ext_word_list=["SAVINGS", "CURRENT"])

class TransactionFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Transaction

    id = factory.Faker('uuid4')
    reference = factory.Faker('sentence', nb_words=1, variable_nb_words=False, ext_word_list=reference_words)
    amount = factory.Faker('pyfloat', min_value=10_000, max_value=299_999, right_digits=2)

class BankTransferFactory(TransactionFactory):

    class Meta:
        model = BankTransfer

class P2PTransferFactory(TransactionFactory):

    class Meta:
        model = P2PTransfer