from django.urls import path
from . import views

urlpatterns = [
    path("", views.idea_list, name="idea_list"),
    path("trending/", views.trending, name="trending"),
    path("submit/", views.idea_create, name="idea_create"),
    path("idea/<slug:slug>/", views.idea_detail, name="idea_detail"),
    path("idea/<slug:slug>/edit/", views.idea_edit, name="idea_edit"),
    path("idea/<slug:slug>/delete/", views.idea_delete, name="idea_delete"),
    path("idea/<slug:slug>/upvote/", views.upvote, name="upvote"),
    path("idea/<slug:slug>/comment/", views.add_comment, name="add_comment"),
    path("user/<str:username>/", views.user_ideas, name="user_ideas"),
    path("accounts/register/", views.register, name="register"),
]
