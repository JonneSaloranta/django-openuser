from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin


class UpdateLastOnlineMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated:
            if (
                not request.user.last_online
                or timezone.now() - request.user.last_online
                > timezone.timedelta(minutes=1)
            ):
                request.user.last_online = timezone.now()
                request.user.save(update_fields=["last_online"])
        return None
