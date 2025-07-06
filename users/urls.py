from django.urls import path

from users.apps import UsersConfig
from users.views import UserCreateAPIView, UserDestroyAPIView, UserListAPIView, UserRetrieveAPIView, UserUpdateAPIView

app_name = UsersConfig.name

urlpatterns = [
    path("user/create/", UserCreateAPIView.as_view(), name="user_create"),
    path("user/", UserListAPIView.as_view(), name="user_list"),
    path("user/<int:pk>/update/", UserUpdateAPIView.as_view(), name="user_update"),
    path(
        "user/<int:pk>/retrieve/",
        UserRetrieveAPIView.as_view(),
        name="user_retrieve",
    ),
    path(
        "user/<int:pk>/destroy/",
        UserDestroyAPIView.as_view(),
        name="user_destroy",
    ),
]
