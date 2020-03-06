import pytest

from .. import models
from . import factories

pytestmark = pytest.mark.django_db


def test_ioi_user_str():
    user: models.IoiUser = factories.IoiUserFactory()
    assert str(user) == user.email


@pytest.mark.parametrize("is_admin", [True, False])
def test_ioi_user_is_staff(is_admin):
    user: models.IoiUser = factories.IoiUserFactory(is_admin=is_admin)
    assert user.is_staff is is_admin
