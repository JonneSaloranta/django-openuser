from django.urls import path

from . import views

app_name = "django_openuser"

urlpatterns = [
    path("<str:username>/", views.profile_details, name="profile_details"),
]