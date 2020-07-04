from firebase_authentication.managers import UserManager as FirebaseUserManager

__all__ = ("WiltUserManager",)


class WiltUserManager(FirebaseUserManager):
    IMMUTABLE_FIELDS = ("id", "email", "is_active", "is_staff", "is_superuser")

    def update_user(self, user, **extra_fields):
        extra_fields = self.__normalize_all(extra_fields)

        for field, value in extra_fields.items():
            if field not in self.IMMUTABLE_FIELDS:
                setattr(user, field, value)

        user.save(using=self._db)
        return user

    def __normalize_all(self, extra_fields):
        """
        Normalized all extra_fields
        if func_normalizers defined in get_func_normalizers
        """
        func_normalizers = self.get_func_normalizers()
        for field_name, func_normalizer in func_normalizers.items():

            if self.is_field_in(extra_fields, filed_name=field_name):

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

    @classmethod
    def normalize_display_name(cls, display_name):
        """
        Normalize the display name address by replacing \\n, \\t and strip.
        """
        display_name = display_name.replace("\n", "")
        display_name = display_name.replace("\t", " ")
        display_name = display_name.strip()
        return display_name

    @staticmethod
    def is_field_in(extra_fields, filed_name):
        """
        Check is filed_name in extra_fields
        """
        return filed_name in extra_fields.keys()
