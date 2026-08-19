"""BarberBook URL configuration."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/auth/', include('accounts.urls')),
    path('api/', include('services.urls')),
    path('api/', include('bookings.urls')),

    # Frontend pages
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('services/', TemplateView.as_view(template_name='services.html'), name='services'),
    path('barbers/', TemplateView.as_view(template_name='barbers.html'), name='barbers'),
    path('barber/<int:pk>/', TemplateView.as_view(template_name='barber_detail.html'), name='barber_detail'),
    path('book/', TemplateView.as_view(template_name='book.html'), name='book'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('register/', TemplateView.as_view(template_name='register.html'), name='register'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    path('admin-panel/', TemplateView.as_view(template_name='admin_panel.html'), name='admin_panel'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'static')
