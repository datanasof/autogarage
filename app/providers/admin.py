from django.contrib import admin
from .models import Provider, Service, BusinessHours, TimeOff
@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display=("id","company_name","slug","city","phone")
admin.site.register(Service); admin.site.register(BusinessHours); admin.site.register(TimeOff)
