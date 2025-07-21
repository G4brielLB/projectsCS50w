
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_post", views.new_post, name="new_post"),
    path("following", views.following, name="following"),
    path("profile/<str:username>", views.profile, name="profile"),
    # API Routes
    path("like/<int:post_id>", views.like, name="like"),
    path("edit_post/<int:post_id>", views.edit_post, name="edit_post"),
    path("follow/<str:username>", views.follow, name="follow"),
]
