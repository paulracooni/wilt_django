from django.contrib import admin
from wilt_backend.models import *
from wilt_backend.models import CheerUpSentence

# Register your models here.
admin.site.register(Til)
admin.site.register(WiltUser)
admin.site.register(CheerUpSentence)
