
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from providers.models import Provider

@login_required
def user_dashboard(request):
    return render(request, 'accounts/user_dashboard.html')

@login_required
def provider_dashboard(request):
    try:
        request.user.provider_profile
    except Provider.DoesNotExist:
        messages.error(request, 'No provider profile is linked to your account yet.')
    return render(request, 'accounts/provider_dashboard.html')

@login_required
@transaction.atomic
def edit_user_view(request):
    if request.method=='POST':
        request.user.first_name = request.POST.get('name','').strip() or request.user.first_name
        request.user.phone = request.POST.get('phone','').strip()
        request.user.city = request.POST.get('city','').strip()
        request.user.save(update_fields=['first_name','phone','city'])
        messages.success(request,'Profile updated.')
        return redirect('user_dashboard')
    return render(request,'accounts/edit_user.html')

@login_required
@transaction.atomic
def edit_provider_view(request):
    try:
        provider = request.user.provider_profile
    except Provider.DoesNotExist:
        messages.error(request,'No provider profile linked.'); return redirect('provider_dashboard')
    if request.method=='POST':
        provider.company_name = request.POST.get('company_name','').strip() or provider.company_name
        provider.phone = request.POST.get('phone','').strip()
        provider.email = request.POST.get('email','').strip().lower()
        provider.address = request.POST.get('address','').strip()
        provider.description = (request.POST.get('description','') or '')[:200]
        provider.latitude = request.POST.get('latitude') or provider.latitude
        provider.longitude = request.POST.get('longitude') or provider.longitude
        provider.save()
        messages.success(request,'Company details updated.')
        return redirect('provider_dashboard')
    return render(request,'accounts/edit_provider.html',{'provider':provider})

@login_required
def search_providers(request):
    return render(request,'accounts/search_providers.html')
