import json
import random
from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta

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
    "LogSearch",
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


class LogSearch(models.Model):
    id = models.AutoField(_("search id"), primary_key=True)
    user = models.ForeignKey(WiltUser, on_delete=models.DO_NOTHING)
    search_entity = models.CharField(_("entity"), max_length=5, null=False)
    search_type = models.CharField(_("type"), max_length=20, null=False)
    keyword = models.CharField(_("keyword"), max_length=50, null=False)
    date_created = models.DateTimeField(_("date created"), **domain_created)

    class Meta:
        db_table = "log_search"
        ordering = ("date_created",)
        verbose_name = _("search log")
        verbose_name_plural = _("search logs")


class Plant(models.Model):
    id = models.AutoField(_("plant id"), primary_key=True)
    plant_id = models.SmallIntegerField(_("plant_id"), null=False)
    user = models.ForeignKey(WiltUser, on_delete=models.CASCADE)
    plant_name = models.CharField(_("plant_name"), max_length=10, null=False)
    til_count = models.SmallIntegerField(_("til_count"), null=False)
    til = models.ManyToManyField(Til, related_name="plant_tils")
    satellite = models.CharField(_("satellite"), max_length=255, default=None, null=True, blank=True)
    date_created = models.DateTimeField(_("date created"), **domain_created)
    completed_date = models.DateField(_("completed_date"), default=None, null=True, blank=True)

    class Meta:
        db_table = "plant"
        ordering = ("date_created",)
        verbose_name = _("plant")
        verbose_name_plural = _("plant")

    #plant를 생성하는 function
    @classmethod
    def update_plant_or_create(cls, user):
        plant_list = Plant.objects.filter(user=user)
        try:
            if plant_list.exists():
                # 30개가 완성된 것은 더 이상 건드리지 않고, 나머지 생성 중인 것만 가지고 와서 fix해준다.
                last_plant = plant_list.last()
                # 마지막이 몇 번째 plant인지 파악
                plant_id = last_plant.plant_id
                Plant.create_plant(user, plant_id)
            else:
                # 처음 생성하는 사람은 모든 것 다시 생성
                Plant.create_plant(user, 0)
        except Exception as e:
            print('create plant excepiton occur',str(e))
            return False

        return True


    @classmethod
    def create_plant(cls, user, plant_id):
        print('create_plant', user, plant_id)
        cycle_count = 30
        user_til_list = Til.objects.filter(user=user, is_active=True).order_by('date_created').prefetch_related("tags")
        total_count = int(len(user_til_list)/30) # 70개면 2개 행성 완성 가능
        # plant_id로 현재 행성 숫자 파악가능 plant_id가 2이면 현재 행성은 2개이다.
        # check_count의 시작은 마지막 행성의 count부터 시작해야 한다.
        if user_til_list:
            for i in range(plant_id, total_count+1):
                # plant_id = 0부터 시작한다.
                user_last_plant = Plant.objects.filter(user=user).last()
                check_count = user_last_plant.til_count if user_last_plant else 0
                # satellite를 string list로 저장

                satellite_list = json.loads(user_last_plant.satellite.replace("'","\"")) if user_last_plant else list()
                til_count = user_last_plant.til_count if user_last_plant else 0
                # 마지막 til이 작성된 시간이 complete_time이다.
                last_til = None
                plant = user_last_plant

                for til in user_til_list[cycle_count*i+check_count:cycle_count*(i+1)]:
                    if check_count % 30 == 0:
                        plant = Plant()
                        plant.user = user
                        from string import ascii_uppercase
                        alpha_list = list(ascii_uppercase)
                        plant_name = "{}{}".format(alpha_list[i],str(til.date_created)[5:10].replace("-",""))
                        plant.plant_name = plant_name
                        plant.til_count = 0
                        plant.plant_id = i
                        plant.save()

                        # plant를 해당 plant로 바꿔주기
                        plant = Plant.objects.filter(user=user).last()

                    # 이제 위성 파악하자.
                    check_count += 1
                    til_count += 1

                    # many to many til 엮기 (중복으로 엮일 수 있는지도 파악해봐야한다.) => 먼저 plant id가 나와야 한다.
                    plant.til.add(til)
                    last_til = til

                    # 최신순으로 태그 정렬
                    for tag in til.tags.all():
                        tag_exists = False
                        print('tag' , tag.name)
                        for i, satellite in enumerate(satellite_list):

                            satellite_tag = list(satellite.keys())[0]
                            print(i, satellite_tag)

                            if tag.name == satellite_tag:
                                tag_exists = True
                                tag_count = satellite_list[i][satellite_tag] + 1
                                satellite_list[i][satellite_tag] = tag_count
                                temp_satellite = satellite_list.pop(i)

                                # 정렬 하기
                                for j, satellite in enumerate(satellite_list):

                                    satellite_tag = list(satellite.keys())[0]
                                    print(123, j, satellite_tag)
                                    if satellite_list[j][satellite_tag] <= tag_count:
                                        satellite_list.insert(j, temp_satellite)
                                        break

                                break

                        if not tag_exists:
                            # 해당 태그가 존재하지 않으면 생성하기
                            temp_satellite = dict()
                            temp_satellite[tag.name] = 1
                            satellite_list.append(temp_satellite)


                plant.satellite = str(satellite_list)
                plant.til_count = til_count

                if last_til:
                    plant.completed_date = last_til.date_created

                plant.save()
        else:
            return None


class CheerUpSentence(models.Model):
    CHEERUP = 0
    GETANGRY = 1

    type = (
        (CHEERUP, '일반 응원문구'),
        (GETANGRY, '5일간 작성하지 않을 때 문구')
    )

    id = models.AutoField(_("cheerup id"), primary_key=True)
    type = models.SmallIntegerField(_("type"), choices=type, default=0, help_text='문구 타입을 설정해주세요')
    text = models.CharField(_("text"), max_length=255)
    start_count = models.SmallIntegerField(_("start_count"), default=0)
    end_count = models.SmallIntegerField(_("end_count"))

    @classmethod
    def get_cheerup_sentence(cls, user):
        today = datetime.now().date()

        user_last_plant = Plant.objects.filter(user=user).last()

        # 5일간 작성하지 않았을 때
        if user_last_plant.completed_date + timedelta(days=5) <= today:
            sentence_list = CheerUpSentence.objects.filter(type=CheerUpSentence.GETANGRY)

        else:
            # 마지막 plant til_count
            til_count = user_last_plant.til_count
            sentence_list = CheerUpSentence.objects.filter(type=CheerUpSentence.CHEERUP, start_count__lte=til_count, end_count__gte=til_count)

        # 랜덤번호 추출
        random_num = random.randint(0, len(sentence_list)-1)

        # 문구 추철
        try:
            text = sentence_list[random_num].text
        except Exception as e:
            print('get_text exception occur',str(e))
            text = None

        return text


