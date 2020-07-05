__all__ = ("WiltUser",)

from django.db import models
from django.utils.translation import gettext_lazy as _

from firebase_authentication.models import User as FirebaseUser

from wilt_user.managers import WiltUserManager

# Create your models here.

nullable = dict(null=True, blank=True)


class WiltUser(FirebaseUser):
    """
    Inherited from firebase_authentication.models.User

    # Firebase mapped attribute
    "id": "aIaAULGfCxXgaDiOfNGPyT8h0ND3",
    "display_name": "아돌프",
    "email": "adolphlee39@gmail.com",

    # Django permission attribute
    "is_active": false,
    "is_staff": false,
    "is_superuser": false

    Define attribute for Wilt user
    "company_name"
    "job_title"
    "career_year"
    +
    "description"
    "web_link"
    """

    company_name = models.CharField(_("company name"), max_length=20, **nullable)

    job_title = models.CharField(_("job title"), max_length=20, **nullable)

    career_year = models.DecimalField(
        _("company name"), max_digits=3, decimal_places=0, **nullable
    )

    description = models.TextField(_("user description"), **nullable)

    web_link = models.TextField(_("web link"), **nullable)

    objects = WiltUserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
