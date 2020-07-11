from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from wilt_user.models import WiltUser

__all__ = (
    "Tag",
    "Til",
    "Clap",
    "Bookmark",
)

# ////////////////////////////////////////////////////////////
# Define Models
# ////////////////////////////////////////////////////////////
CATEGORY_CHOICES = [
    ("PL", _("Plan")),
    ("DS", _("Design")),
    ("DV", _("Develop")),
    ("MK", _("Marketing")),
    ("DT", _("Data")),
]


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

    date_created = models.DateTimeField(
        _("date created"), default=timezone.now, editable=False
    )

    # objects = TilManager()

    class Meta:
        # db_table = "til"
        verbose_name = _("til")
        verbose_name_plural = _("tils")


class Clap(models.Model):
    id = models.AutoField(_("clap id"), primary_key=True)
    user = models.ForeignKey(WiltUser, on_delete=models.CASCADE)
    til = models.ForeignKey(Til, on_delete=models.CASCADE)
    date_created = models.DateTimeField(
        _("date created"), default=timezone.now, editable=False
    )

    class Meta:
        # db_table = "clap"
        verbose_name = _("clap")
        verbose_name_plural = _("claps")
        unique_together = (("user", "til",),)


class Bookmark(models.Model):
    id = models.AutoField(_("bookmark id"), primary_key=True)
    user = models.ForeignKey(WiltUser, on_delete=models.CASCADE)
    til = models.ForeignKey(Til, on_delete=models.CASCADE)
    date_created = models.DateTimeField(
        _("date created"), default=timezone.now, editable=False
    )

    class Meta:
        # db_table = "bookmark"
        verbose_name = _("bookmark")
        verbose_name_plural = _("bookmarks")
        unique_together = (("user", "til",),)
