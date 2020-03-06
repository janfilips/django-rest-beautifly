from uuid import uuid4

from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class UserManager(BaseUserManager):
    def create_user(self, email, nickname="", password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(email=self.normalize_email(email))
        user.nickname = nickname
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(email, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class IoiUser(AbstractBaseUser):
    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    email = models.EmailField(verbose_name="email address", max_length=255, unique=True)
    nickname = models.CharField(max_length=128, blank=True)
    jwt_secret = models.UUIDField(default=uuid4)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_investor = models.BooleanField(default=False)
    created = models.DateField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"

    class Meta:
        db_table = "users_users"
        verbose_name = "IOI user"
        verbose_name_plural = "IOI users"

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        # Simplest possible answer: Yes, always
        return True

    def jwt_get_secret_key(user_model):
        return user_model.jwt_secret

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        # Simplest possible answer: All admins are staff
        return self.is_admin
