from django.contrib.auth.models import UserManager as DefaultUserManager

from firebase_admin import auth
from firebase_authentication.exceptions import UserNotFound
from firebase_authentication.exceptions import UserEmailNotMatched

__all__ = ("UserManager",)


class UserManager(DefaultUserManager):
    def register_user(self, id, email, password=None, **extra_fields):

        self._check_valid_register(id, email)

        extra_fields.setdefault("is_active", True)
        user = self.model(id=id, email=email, **extra_fields)
        user.save(using=self._db)
        return user

    @staticmethod
    def _check_valid_register(uid, email):
        try:
            user = auth.get_user(uid)
        except Exception:
            raise UserNotFound

        if user.email != email:
            raise UserEmailNotMatched

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        auth_user = auth.create_user(
            email=email,
            email_verified=False,
            password=password,
            display_name=extra_fields.get("display_name", ""),
            disabled=False,
        )
        user = self.model(id=auth_user.uid, email=email, **extra_fields)
        user.save(using=self._db)
        return user
