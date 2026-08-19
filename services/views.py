from rest_framework import viewsets, filters
from .models import Service, Barber
from .serializers import ServiceSerializer, BarberSerializer
from .permissions import IsAdminOrReadOnly


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'category']
    ordering_fields = ['price', 'duration_minutes', 'name', 'created_at']
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        cat = self.request.query_params.get('category')
        active = self.request.query_params.get('active')
        if cat:
            qs = qs.filter(category=cat)
        if active is not None:
            qs = qs.filter(is_active=(active.lower() == 'true'))
        return qs


class BarberViewSet(viewsets.ModelViewSet):
    queryset = Barber.objects.prefetch_related('services').all()
    serializer_class = BarberSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['display_name', 'specialty', 'bio']
    ordering_fields = ['display_name', 'years_experience', 'rating']
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        active = self.request.query_params.get('active')
        service_id = self.request.query_params.get('service')
        if active is not None:
            qs = qs.filter(is_active=(active.lower() == 'true'))
        if service_id:
            qs = qs.filter(services__id=service_id)
        return qs.distinct()
