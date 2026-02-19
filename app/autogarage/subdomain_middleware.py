
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from providers.models import Provider

class SubdomainProviderMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.provider = None
        host = request.get_host().split(':')[0]
        base = settings.BASE_DOMAIN
        if host == base or not host.endswith(base):
            return
        sub = host[:-(len(base)+1)]
        if sub and sub not in ('www',):
            try:
                request.provider = Provider.objects.get(slug=sub)
            except Provider.DoesNotExist:
                request.provider = None
