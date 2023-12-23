# URL mappings for the posts app.

from django.urls import path

from . import views

app_name = "posts"

urlpatterns = [
    path("", views.index, name="index"),
    path("about", views.about, name="about"),
    path("tos", views.tos, name="tos"),
    path("create", views.create, name="create"),
    path("view/<int:post_id>", views.view, name="view"),
    path("comment/<int:post_id>", views.comment, name="comment"),
    path("comment/delete/<int:comment_id>/<int:post_id>", views.delete_comment, name="delete_comment"),
    path("edit/<int:post_id>", views.edit, name="edit"),
    path("user/<int:user_id>", views.view_user, name="view_user"),
    path("user/<str:username>", views.view_user_by_username, name="view_user_by_username"),
    path("login", views.login_view, name="login_view"),
    path("logout", views.logout_view, name="logout_view"),
    path("reset_password", views.reset_password, name="reset_password"),
]
