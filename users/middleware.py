from django.db.models import F
from users.models import Stat
from django.conf import settings


class DemoMiddleware:
    def __init__(self , get_response) -> None:
        self.get_response = get_response
        self.num_exceptions = 0

    def stats(self, os_info):
        if "Windows" in os_info:
            Stat.objects.all().update(win = F( 'win')+1 )
        elif "Mac" in os_info:
            Stat.objects.all().update(mac = F('mac')+1 )
        elif "iPhone" in os_info:
            Stat.objects.all().update(ios = F('ios')+1 )
        elif "Android" in os_info:
            Stat.objects.all().update(android = F('android')+1 )
        else:
            Stat.objects.all().update(oth = F('oth')+1 )

    def __call__(self, request,*args, **kwargs):

        if ('admin' or 'Admin' not in request.path) and (not settings.DEBUG):
            print(settings.DEBUG)
            self.stats(request.META['HTTP_USER_AGENT'])
        response = self.get_response (request)
        return response