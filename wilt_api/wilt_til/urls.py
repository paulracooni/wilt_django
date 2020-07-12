from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from wilt_til import views

urlpatterns = [
    path("", views.FeedListCreate.as_view()),
    path("<int:id>/", views.TilRetrieveUpdateDestroy.as_view()),
    path("<int:id>/bookmarks", views.TilBookmark.as_view()),
    path("<int:id>/claps", views.TilClap.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
