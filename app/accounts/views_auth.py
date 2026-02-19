
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.db import transaction
from django.contrib.auth.decorators import login_required
from accounts.models import User
from providers.models import Provider
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET","POST"])
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email','').strip().lower()
        password = request.POST.get('password','')
        try:
            u = User.objects.get(email__iexact=email)
            if u.check_password(password):
                login(request, u)
                return redirect('provider_dashboard' if u.role==User.Roles.PROVIDER else 'user_dashboard')
            else:
                messages.error(request, 'Invalid email/password')
        except User.DoesNotExist:
            messages.error(request, 'Invalid email/password')
    return render(request, 'accounts/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')

@require_http_methods(["GET","POST"])
@transaction.atomic
def register_user_view(request):
    if request.method == 'POST':
        name = request.POST.get('name','').strip()
        email = request.POST.get('email','').strip().lower()
        password = request.POST.get('password','')
        password2 = request.POST.get('password2','')
        phone = request.POST.get('phone','').strip()
        city = request.POST.get('city','').strip()
        if not all([name,email,password,password2,phone,city]):
            messages.error(request,'Please fill all fields.')
        elif password!=password2:
            messages.error(request,'Passwords do not match.')
        elif User.objects.filter(email__iexact=email).exists():
            messages.error(request,'This mail has already been used for registration. Please <a href="/login/">login</a> or use a different email address.')
        else:
            u = User(username=email, email=email, first_name=name, role=User.Roles.END_USER, phone=phone, city=city)
            u.set_password(password); u.save(); login(request,u)
            return redirect('user_dashboard')
    return render(request, 'accounts/register_user.html')

@require_http_methods(["GET","POST"])
@transaction.atomic
def register_provider_view(request):
    if request.method == 'POST':
        subdomain = request.POST.get('slug','').strip().lower()
        company_name = request.POST.get('company_name','').strip()
        email = request.POST.get('email','').strip().lower()
        password = request.POST.get('password','')
        password2 = request.POST.get('password2','')
        phone = request.POST.get('phone','').strip()
        address = request.POST.get('address','').strip()
        description = (request.POST.get('description','') or '')[:200]
        lat = request.POST.get('latitude'); lng = request.POST.get('longitude')
        if not all([subdomain,company_name,email,password,password2,phone,address,description,lat,lng]):
            messages.error(request,'Please complete all fields and pick your map location.')
        elif password!=password2:
            messages.error(request,'Passwords do not match.')
        elif User.objects.filter(email__iexact=email).exists():
            messages.error(request,'This mail has already been used for registration. Please <a href="/login/">login</a> or use a different email address.')
        elif Provider.objects.filter(slug=subdomain).exists():
            messages.error(request,'Subdomain is already taken. Choose another.')
        else:
            u = User(username=email, email=email, role=User.Roles.PROVIDER)
            u.set_password(password); u.save()
            Provider.objects.create(user=u, company_name=company_name, slug=subdomain,
                                    phone=phone, email=email, address=address,
                                    description=description, latitude=lat, longitude=lng)
            login(request,u)
            return redirect('provider_dashboard')
    return render(request, 'accounts/register_provider.html')
