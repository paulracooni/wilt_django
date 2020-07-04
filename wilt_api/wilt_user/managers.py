from firebase_authentication.managers import UserManager as FirebaseUserManager

__all__ = ("WiltUserManager",)


class WiltUserManager(FirebaseUserManager):
    def update_user(self, user, **extra_fields):
        extra_fields = self.__normalize_all(extra_fields)
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
    def __update_user(user, extra_fields):
        for field, value in extra_fields.items():
            setattr(user, field, value)
        return user
