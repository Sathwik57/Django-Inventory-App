from django.contrib.auth.mixins import AccessMixin

class IsAdmin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)