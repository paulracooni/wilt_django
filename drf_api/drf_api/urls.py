from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from core.views import PestView, PostCreateView, PostListCreateView

urlpatterns = [
    path("api-auth", include("rest_framework.urls")),
    path("admin/", admin.site.urls),
    path("", PestView.as_view(), name="test"),
    path("create/", PostCreateView.as_view(), name="create"),
    path("listcreate/", PostListCreateView.as_view(), name="listcreate"),
    path("api/token", obtain_auth_token, name="obtain-token"),
]
