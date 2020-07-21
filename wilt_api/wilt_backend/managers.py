from django.contrib.auth.models import UserManager as DefaultUserManager

from firebase_admin import auth
from wilt_backend.exceptions import UserNotFound
from wilt_backend.exceptions import UserEmailNotMatched


class UserManager(DefaultUserManager):
    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("display_name", email.split("@")[0])
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("display_name", email.split("@")[0])

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
            display_name=extra_fields.get("display_name", auth.DELETE_ATTRIBUTE),
            disabled=False,
        )
        user = self.model(id=auth_user.uid, email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def update_user(self, user, **extra_fields):
        extra_fields = self.__normalize_all(extra_fields)
        auth.update_user(
            uid=user.id,
            display_name=extra_fields.get("display_name", user.display_name),
            disabled=False,
            photo_url=extra_fields.get("picture", user.picture),
        )
        user = self.__update_user(user, extra_fields)

        user.save(using=self._db)
        return user

    def __normalize_all(self, extra_fields):
        """
        Normalized all extra_fields
        if func_normalizers defined in get_func_normalizers
        """

        func_normalizers = self.get_func_normalizers()

        for field_name, func_normalizer in func_normalizers.items():

            if field_name in extra_fields.keys():

                field_value = extra_fields[field_name]
                extra_fields[field_name] = func_normalizer(field_value)

        return extra_fields

    @classmethod
    def get_func_normalizers(cls):
        """
        Define normalizer functions wilt field name.
        """
        func_normalizers = dict(
            email=cls.normalize_email, display_name=cls.normalize_display_name
        )
        return func_normalizers

    @staticmethod
    def normalize_display_name(display_name):
        """
        Normalize the display name address by replacing \\n, \\t and strip.
        """
        display_name = display_name.replace("\n", "")
        display_name = display_name.replace("\t", " ")
        display_name = display_name.strip()
        return display_name

    @staticmethod
    def __update_user(user, extra_fields):
        for field, value in extra_fields.items():
            setattr(user, field, value)
        return user
