import factory


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "users.User"
        django_get_or_create = ("username",)

    id = factory.Faker("uuid4")
    username = factory.Sequence(lambda n: f"testuser{n}")
    password = factory.Faker(
        "password",
        length=10,
        special_chars=True,
        digits=True,
        upper_case=True,
        lower_case=True,
    )
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True
    is_staff = False


class AllBankFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "banks.AllBanks"
        django_get_or_create = ["name"]


class BankFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "banks.Bank"
        django_get_or_create = ("owner", "bank")

    owner = factory.SubFactory(UserFactory)
    bank = factory.SubFactory(AllBankFactory)
