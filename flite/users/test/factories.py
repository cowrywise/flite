import factory

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


class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'users.Transaction'


    id = factory.Faker('uuid4')
    owner = factory.SubFactory(UserFactory)
    status = factory.Faker('text')
    reference = factory.Faker('text')
    amount = 100.00
    new_balance = 10.00

class BalanceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'users.Balance'

    id = factory.Faker('uuid4')
    owner = factory.SubFactory(UserFactory)
    available_balance = 300000.00