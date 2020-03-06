import factory
from django.contrib.auth.hashers import make_password

from .. import models


class IoiUserFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.IoiUser
        django_get_or_create = ["email"]

    email = factory.Faker("email")
    # set unusable password
    password = factory.LazyFunction(lambda: make_password(None))
