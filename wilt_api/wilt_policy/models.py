import datetime
from django.db import models
from django.utils import timezone
from django.utils import dateformat
from django.utils.translation import gettext_lazy as _
from datetime import datetime

# Create your models here.

nullable = dict(null=True, blank=True)
domain_autotime = dict(default=timezone.now, editable=False)
domain_token = dict(max_length=50)
domain_option = dict(max_length=20)


class Policy(models.Model):
    id = models.AutoField(primary_key=True)
    date_created = models.DateTimeField(_("date created"), **domain_autotime)

    terms_of_service = models.TextField(_("Terms of Service"), **nullable)
    privacy_statement = models.TextField(_("Privacy Statement"), **nullable)

    class Meta:
        db_table = "wilt_policy"
        ordering = ["-date_created"]

    def __str__(self):

        return dateformat.format(self.date_created, "c")


class S3AuthInfo(models.Model):
    id = models.AutoField(primary_key=True)
    date_created = models.DateTimeField(_("date created"), **domain_autotime)

    access_key_id = models.CharField(_("access key id"), **domain_token)
    secret_key_id = models.CharField(_("secret key id"), **domain_token)
    region = models.CharField(_("region"), **domain_option)
    s3_endpoint = models.URLField(_("s3 endpont"))
    algorithm = models.CharField(_("algorithm"), **domain_option)
    acl = models.CharField(_("acl"), **domain_option)

    class Meta:
        db_table = "S3_auth_info"
        ordering = ["-date_created"]

    def __str__(self):
        return dateformat.format(self.date_created, "c")
