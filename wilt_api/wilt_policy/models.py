import datetime
from django.db import models
from django.utils import timezone
from django.utils import dateformat
from django.utils.translation import gettext_lazy as _

# Create your models here.

nullable = dict(null=True, blank=True)
domain_autotime = dict(default=timezone.now, editable=False)


class Policy(models.Model):
    id = models.AutoField(primary_key=True)

    terms_of_service = models.TextField(_("Terms of Service"), **nullable)

    privacy_statement = models.TextField(_("Privacy Statement"), **nullable)

    date_created = models.DateTimeField(_("date created"), **domain_autotime)

    class Meta:
        db_table = "wilt_policy"
        ordering = ["-date_created"]

    def __str__(self):
        return dateformat.format(self.date_created, "%Y-%m-%d %H:%M:%S")
