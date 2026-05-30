from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext_lazy as _

User = get_user_model()


@login_required
def profile_details(request, username):
    user_profile = get_object_or_404(User, username=username)


    context = {
        "title": _("Profile"),
        "profile": user_profile,
    }
    return render(request, "django_openuser/details.html", context=context)
