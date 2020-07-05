from django.db import models
from django.utils.translation import gettext_lazy as _

from wilt_user.models import WiltUser

# Create your models here.
CATEGORY_CHOICES = [
    ("PL", _("Plan")),
    ("DS", _("Design")),
    ("DV", _("Develop")),
    ("MK", _("Marketing")),
    ("DT", _("Data")),
]


class Til(models.Model):

    id = models.AutoField(_("til id"), primary_key=True)

    author = models.ForeignKey(_("author"), WiltUser, on_delete=models.CASCADE)

    category = models.CharField(_("category"), max_length=2, choices=CATEGORY_CHOICES)

    title = models.TextField(_("title"))

    content = models.TextField(_("content"))

    date_created = models.DateTimeField(_("date created"), default=timezone.now)

    is_public = models.BooleanField(_("public"), default=True,)

    class Meta:
        # db_table = "til"
        verbose_name = _("til")
        verbose_name_plural = _("tils")