__all__ = ("WiltUser",)

from django.db import models
from django.utils.translation import gettext_lazy as _

from firebase_authentication.models import User as FirebaseUser

from firebase_authentication.managers import UserManager as FirebaseUserManager

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

    objects = FirebaseUserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")


class UserFollow(models.Model):
    user_id = models.ForeignKey(
        WiltUser, related_name="following", on_delete=models.CASCADE
    )
    following_user_id = models.ForeignKey(
        WiltUser, related_name="follower", on_delete=models.CASCADE
    )
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = ("user_id", "following_user_id")
        ordering = ["-date_created"]

    def __str__(self):
        f"{self.user_id} follows {self.following_user_id}"
