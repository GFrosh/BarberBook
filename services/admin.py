from django.contrib import admin
from .models import Service, Barber


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'duration_minutes', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')
    list_editable = ('is_active', 'price', 'duration_minutes')


@admin.register(Barber)
class BarberAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'specialty', 'years_experience', 'rating', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('display_name', 'specialty')
    filter_horizontal = ('services',)
