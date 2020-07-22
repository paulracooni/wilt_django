from django.db import models
from django.utils import timezone

from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from wilt_backend.managers import UserManager

# Models defined as bellow.
__all__ = (
    "WiltUser",
    "UserFollow",
    "Tag",
    "Til",
    "Clap",
    "Bookmark",
    "Comment",
)

nullable = dict(null=True, blank=True)
domain_id = dict(max_length=28, primary_key=True, db_index=True, unique=True)
domain_name = dict(max_length=20, unique=True, null=True, blank=True)
domain_parent = dict(null=True, blank=True, on_delete=models.CASCADE)
domain_created = dict(default=timezone.now, editable=False)


# ////////////////////////////////////////////////////////////
JOBTITLE_CHOICES = [
    ("PL", _("Planer")),
    ("DS", _("Designer")),
    ("DV", _("Developer")),
    ("MK", _("Marketer")),
    ("DT", _("DataScientist")),
]

CATEGORY_CHOICES = [
    ("PL", _("Plan")),
    ("DS", _("Design")),
    ("DV", _("Develop")),
    ("MK", _("Marketing")),
    ("DT", _("Data")),
]


class WiltUser(AbstractUser):

    username = None
    first_name = None
    last_name = None

    id = models.CharField(**domain_id)

    display_name = models.CharField(_("display name"), **domain_name)

    email = models.EmailField(_("email address"), unique=True)

    picture = models.URLField(_("picture"), **nullable)

    company_name = models.CharField(_("company name"), max_length=20, **nullable)

    job_title = models.CharField(
        _("job title"), max_length=2, choices=JOBTITLE_CHOICES, **nullable
    )

    career_year = models.DecimalField(
        _("company name"), max_digits=3, decimal_places=0, **nullable
    )

    description = models.TextField(_("user description"), **nullable)

    web_link = models.TextField(_("web link"), **nullable)

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "wilt_user"
        verbose_name = _("user")
        verbose_name_plural = _("users")


class UserFollow(models.Model):
    user_id = models.ForeignKey(
        WiltUser, related_name="following", on_delete=models.CASCADE
    )
    following_user_id = models.ForeignKey(
        WiltUser, related_name="follower", on_delete=models.CASCADE
    )
    date_created = models.DateTimeField(_("date created"), **domain_created)

    class Meta:
        db_table = "user_follow"
        unique_together = ("user_id", "following_user_id")
        ordering = ["-date_created"]

    def __str__(self):
        f"{self.user_id} follows {self.following_user_id}"


class Tag(models.Model):

    name = models.CharField(max_length=50)

    class Meta:
        db_table = "tag"
        verbose_name = _("태그")
        verbose_name_plural = _("태그")

    def __str__(self):

        return "Tag[id: {id}, text: {text}]".format(id=self.id, text=self.name)


class Til(models.Model):

    id = models.AutoField(_("til id"), primary_key=True)

    user = models.ForeignKey(WiltUser, on_delete=models.CASCADE)

    category = models.CharField(_("category"), max_length=2, choices=CATEGORY_CHOICES)

    title = models.TextField(_("title"))

    content = models.TextField(_("content"))

    is_public = models.BooleanField(_("public"), default=True,)

    is_active = models.BooleanField(_("is active"), default=True,)

    tags = models.ManyToManyField(Tag, related_name="til_tags")

    date_created = models.DateTimeField(_("date created"), **domain_created)

    # objects = TilManager()

    class Meta:
        db_table = "til"
        verbose_name = _("til")
        verbose_name_plural = _("tils")


class Clap(models.Model):
    id = models.AutoField(_("clap id"), primary_key=True)
    user = models.ForeignKey(WiltUser, on_delete=models.CASCADE)
    til = models.ForeignKey(Til, on_delete=models.CASCADE)
    date_created = models.DateTimeField(_("date created"), **domain_created)

    class Meta:
        db_table = "clap"
        verbose_name = _("clap")
        verbose_name_plural = _("claps")
        unique_together = (("user", "til",),)


class Bookmark(models.Model):
    id = models.AutoField(_("bookmark id"), primary_key=True)
    user = models.ForeignKey(WiltUser, on_delete=models.CASCADE)
    til = models.ForeignKey(Til, on_delete=models.CASCADE)
    date_created = models.DateTimeField(_("date created"), **domain_created)

    class Meta:
        db_table = "bookmark"
        verbose_name = _("bookmark")
        verbose_name_plural = _("bookmarks")
        unique_together = (("user", "til",),)


class Comment(models.Model):

    id = models.AutoField(_("comment id"), primary_key=True)
    user = models.ForeignKey(WiltUser, on_delete=models.CASCADE)
    til = models.ForeignKey(Til, on_delete=models.CASCADE)
    content = models.TextField(_("content"))
    is_active = models.BooleanField(_("is active"), default=True,)
    date_created = models.DateTimeField(_("date created"), **domain_created)
    parent = models.ForeignKey("self", related_name="replies", **domain_parent)

    class Meta:
        db_table = "comment"
        ordering = ("date_created",)
        verbose_name = _("comment")
        verbose_name_plural = _("comments")
