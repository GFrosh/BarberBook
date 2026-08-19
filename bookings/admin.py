from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'barber', 'service', 'appointment_date',
                    'start_time', 'end_time', 'status', 'total_price')
    list_filter = ('status', 'appointment_date', 'barber', 'service__category')
    search_fields = ('customer__username', 'barber__display_name', 'service__name')
    date_hierarchy = 'appointment_date'
    list_editable = ('status',)
