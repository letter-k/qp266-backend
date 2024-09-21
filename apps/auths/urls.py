from django.urls import path

from apps.auths import views

urlpatterns = [
    path("login/", views.ObtainAuthToken.as_view(), name="login"),
]
