from rest_framework.routers import DefaultRouter
from .views import ServiceViewSet, BarberViewSet

router = DefaultRouter()
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'barbers', BarberViewSet, basename='barber')

urlpatterns = router.urls
