from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'appointments', views.AppointmentViewSet, basename='appointment')

urlpatterns = router.urls + [
    path('admin/appointments', views.admin_appointments, name='admin-appointments'),
    path('admin/appointments/<int:pk>/status', views.admin_update_status, name='admin-update-status'),
    path('admin/stats', views.admin_stats, name='admin-stats'),
    path('barbers/<int:pk>/busy', views.barber_busy_slots, name='barber-busy'),
    path('barbers/<int:pk>/slots', views.barber_available_slots, name='barber-slots'),
]
