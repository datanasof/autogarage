# autogarage/subdomain_middleware.py
from django.conf import settings
from providers.models import Provider

class SubdomainMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.base_domain = getattr(settings, "BASE_DOMAIN", "")

    def __call__(self, request):
        request.provider = None
        host = request.get_host().split(":")[0]
        # expected: <subdomain>.<base_domain>
        if self.base_domain and host.endswith(self.base_domain):
            maybe = host[: -(len(self.base_domain) + 1)]
            if maybe and maybe != "www":
                try:
                    request.provider = Provider.objects.get(slug=maybe)
                except Provider.DoesNotExist:
                    request.provider = None
        return self.get_response(request)