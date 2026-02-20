
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.conf import settings

def home(request):
    return render(request,'home.html')

def spa_view(request, path=None):
    """Serve the React SPA index.html for client-side routing."""
    import json
    index_path = getattr(settings, 'FRONTEND_DIST', None) or (settings.BASE_DIR.parent / 'frontend' / 'dist')
    index_file = index_path / 'index.html'
    if not index_file.exists():
        return HttpResponse(
            '<p>Frontend not built. Run: <code>cd frontend && npm install && npm run build</code></p>',
            status=503,
            content_type='text/html',
        )
    with open(index_file, encoding='utf-8') as f:
        html = f.read()
    # Inject runtime config (e.g. Google Maps API key from Django/env) so SPA can use it
    api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', '') or ''
    config_script = (
        '<script>window.__AUTOGARAGE_CONFIG__='
        + json.dumps({'googleMapsApiKey': api_key})
        + ';</script>'
    )
    if '</head>' in html:
        html = html.replace('</head>', config_script + '\n</head>', 1)
    else:
        html = html.replace('<body>', '<body>' + config_script, 1)
    return HttpResponse(html, content_type='text/html')

def public_config(request):
    """Public runtime config for the SPA (e.g. Google Maps API key). No auth required."""
    return JsonResponse({
        "googleMapsApiKey": getattr(settings, "GOOGLE_MAPS_API_KEY", "") or "",
    })

def public_provider(request):
    provider = getattr(request, 'provider', None)
    if not provider:
        return render(request,'public_provider.html',{'error':'No provider context (subdomain missing or invalid).'})
    services = provider.services.filter(is_active=True).order_by('name')
    return render(request,'public_provider.html',{'provider':provider,'services':services})

@login_required
def calendar_view(request):
    return render(request,'calendar.html')
