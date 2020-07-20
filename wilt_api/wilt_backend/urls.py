from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from wilt_backend.views import view_tils
from wilt_backend.views import view_users

urlpatterns = [
    # Til related endpoints
    path("tils/", view_tils.FeedListCreate.as_view()),
    path("tils/<int:id>/", view_tils.TilRetrieveUpdateDestroy.as_view()),
    path("tils/<int:id>/bookmarks/", view_tils.TilBookmark.as_view()),
    path("tils/<int:id>/claps/", view_tils.TilClap.as_view()),
    # User related endpoints
    path("users/", view_users.UserCheck.as_view()),
    path("users/<str:id>/", view_users.UserDetail.as_view()),
    path("users/<str:id>/claps/", view_users.UserClaps.as_view()),
    path("users/<str:id>/bookmarks/", view_users.UserBookmark.as_view()),
    path("users/<str:id>/tags/", view_users.UserTag.as_view()),
    path("users/<str:id>/following/", view_users.UserFollowing.as_view()),
    path("users/<str:id>/followers/", view_users.UserFollowers.as_view()),
    path("users/<str:id>/tils/", view_users.UserTils.as_view()),
    path("users/<str:id>/totalcount/", view_users.UserTotalCount.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)