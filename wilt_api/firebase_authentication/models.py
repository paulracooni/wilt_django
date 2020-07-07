from django.db import models

from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from firebase_authentication.managers import UserManager

__all__ = ("User",)


domain_id = dict(max_length=28, primary_key=True, db_index=True, unique=True)
domain_name = dict(max_length=20, unique=True, null=True, blank=True)


class User(AbstractUser):
    username = None
    first_name = None
    last_name = None

    id = models.CharField(**domain_id)
    display_name = models.CharField(_("display name"), **domain_name)
    email = models.EmailField(_("email address"), unique=True)

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def get_full_name(self):
        return self.display_name or self.email

    def get_short_name(self):
        return self.display_name.partition(" ")[0] or self.email
