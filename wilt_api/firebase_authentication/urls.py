from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from firebase_authentication import views

urlpatterns = [
    path("", views.UserCheck.as_view()),
    path("<str:uid>", views.UserDetail.as_view()),
    # path('snippets/<int:pk>/', views.SnippetDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
