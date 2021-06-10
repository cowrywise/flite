import factory
from flite.users.test.factories import UserFactory


class AllBankFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'account.AllBanks'
    name = factory.Faker('name')
    acronym = factory.Faker('word')
    bank_code = factory.Faker('word')


class BankFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'account.Bank'


    owner = factory.SubFactory(UserFactory)
    bank = factory.SubFactory(AllBankFactory)
    account_name =  factory.Faker('name')
    account_number =  factory.Faker('random_number')
    account_type =  'Saving'


class CardFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'account.Card'
        django_get_or_create = ('id',)
    id = factory.Faker('uuid4')
    owner = factory.SubFactory(UserFactory)
   
    authorization_code =  factory.Faker('word')
    ctype =  factory.Faker('word')
    cbin =  factory.Faker('word')
    cbrand =  factory.Faker('word')
    name =  factory.Faker('name')
    number =  factory.Faker('random_number')
    expiry_month =  '12'
    expiry_year =  '2022'
    is_active = True
    is_deleted = False