from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from wilt_backend.views import view_tils
from wilt_backend.views import view_users
from wilt_backend.views import view_search
from wilt_policy import views as view_policy

urlpatterns = [
    # Til related endpoints
    path("tils/", view_tils.FeedListCreate.as_view()),
    path("tils/<int:id>/", view_tils.TilRetrieveUpdateDestroy.as_view()),
    path("tils/<int:til_id>/claps/", view_tils.TilClap.as_view()),
    path("tils/<int:til_id>/comments/", view_tils.TilComment.as_view()),
    path(
        "tils/<int:til_id>/comments/<int:comment_id>/",
        view_tils.TilCommentUpdateDestroy.as_view(),
    ),
    path("tils/<int:til_id>/bookmarks/", view_tils.TilBookmark.as_view()),
    # User related endpoints
    path("users/", view_users.UserCheck.as_view()),
    path("users/<str:user_id>/", view_users.UserDetail.as_view()),
    path("users/<str:user_id>/claps/", view_users.UserClaps.as_view()),
    path("users/<str:user_id>/bookmarks/", view_users.UserBookmark.as_view()),
    path("users/<str:user_id>/categories/", view_users.UserCategories.as_view()),
    path("users/<str:user_id>/plant/ongoing/", view_users.UserGoingPlant.as_view()),
    path("users/<str:user_id>/plant/finish/", view_users.UserFinishPlant.as_view()),
    path("users/<str:user_id>/tags/", view_users.UserTag.as_view()),
    path("users/<str:user_id>/following/", view_users.UserFollowing.as_view()),
    path("users/<str:user_id>/followers/", view_users.UserFollowers.as_view()),
    path("users/<str:user_id>/tils/", view_users.UserTils.as_view()),
    path("users/<str:user_id>/totalcount/", view_users.UserTotalCount.as_view()),
    # Search related endpoints
    path("search/tils/", view_search.SearchTils.as_view()),
    path("search/hot-tags/", view_search.HotTagRetrive.as_view()),
    path("search/hot-keyword/", view_search.HotKeywordRetrive.as_view()),
    # path("search/users")
    # Policy retrive endpoints
    path("policy/", view_policy.PolicyRetrieve.as_view()),
    path("s3auth/", view_policy.S3AuthInfoRetrieve.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
