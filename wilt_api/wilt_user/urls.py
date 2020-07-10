from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from wilt_user import views

urlpatterns = [
    path("", views.UserCheck.as_view()),
    path("<str:id>/", views.UserDetail.as_view()),
    path("<str:id>/claps/", views.UserClaps.as_view()),
    path("<str:id>/bookmarks", views.UserBookmark.as_view()),
    path("<str:id>/tags", views.UserTag.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
