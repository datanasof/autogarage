
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request,'home.html')

def public_provider(request):
    provider = getattr(request, 'provider', None)
    if not provider:
        return render(request,'public_provider.html',{'error':'No provider context (subdomain missing or invalid).'})
    services = provider.services.filter(is_active=True).order_by('name')
    return render(request,'public_provider.html',{'provider':provider,'services':services})

@login_required
def calendar_view(request):
    return render(request,'calendar.html')
