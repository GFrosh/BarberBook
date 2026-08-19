from datetime import datetime, timedelta, date as date_cls

from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from services.models import Barber, Service
from .models import Appointment
from .serializers import AppointmentSerializer, AdminStatusSerializer
from .permissions import IsOwnerBarberOrAdmin, IsAdminUserRole


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerBarberOrAdmin]

    def get_queryset(self):
        u = self.request.user
        qs = Appointment.objects.select_related('barber', 'customer', 'service').all()
        is_admin = getattr(u, 'is_admin_role', False) or u.is_staff
        if not is_admin:
            if getattr(u, 'is_barber_role', False):
                qs = qs.filter(barber__user=u) | qs.filter(customer=u)
                qs = qs.distinct()
            else:
                qs = qs.filter(customer=u)
        # filters
        params = self.request.query_params
        for key, field in [('status', 'status'), ('barber', 'barber_id'),
                           ('service', 'service_id'), ('date', 'appointment_date')]:
            if params.get(key):
                qs = qs.filter(**{field: params[key]})
        return qs

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user, status=Appointment.Status.PENDING)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsOwnerBarberOrAdmin])
    def cancel(self, request, pk=None):
        appt = self.get_object()
        if appt.status in [Appointment.Status.COMPLETED, Appointment.Status.CANCELLED, Appointment.Status.NO_SHOW]:
            return Response({'detail': f'Cannot cancel a {appt.status} appointment.'},
                            status=status.HTTP_400_BAD_REQUEST)
        appt.status = Appointment.Status.CANCELLED
        appt.save()
        return Response(AppointmentSerializer(appt, context={'request': request}).data)


# ----- Admin endpoints -----

@api_view(['GET'])
@permission_classes([IsAdminUserRole])
def admin_appointments(request):
    qs = Appointment.objects.select_related('barber', 'customer', 'service').all().order_by('-created_at')
    if request.query_params.get('status'):
        qs = qs.filter(status=request.query_params['status'])
    return Response(AppointmentSerializer(qs, many=True, context={'request': request}).data)


@api_view(['PATCH'])
@permission_classes([IsAdminUserRole])
def admin_update_status(request, pk):
    try:
        appt = Appointment.objects.get(pk=pk)
    except Appointment.DoesNotExist:
        return Response({'detail': 'Not found.'}, status=404)
    s = AdminStatusSerializer(appt, data=request.data, partial=True); s.is_valid(raise_exception=True)
    appt.status = s.validated_data['status']
    appt.save()
    return Response(AppointmentSerializer(appt, context={'request': request}).data)


@api_view(['GET'])
@permission_classes([IsAdminUserRole])
def admin_stats(request):
    total = Appointment.objects.count()
    pending = Appointment.objects.filter(status=Appointment.Status.PENDING).count()
    confirmed = Appointment.objects.filter(status=Appointment.Status.CONFIRMED).count()
    cancelled = Appointment.objects.filter(status=Appointment.Status.CANCELLED).count()
    completed = Appointment.objects.filter(status=Appointment.Status.COMPLETED).count()
    revenue = Appointment.objects.filter(
        status__in=[Appointment.Status.CONFIRMED, Appointment.Status.COMPLETED]
    ).aggregate(total=Sum('total_price'))['total'] or 0

    today = timezone.now().date()
    today_count = Appointment.objects.filter(appointment_date=today).count()

    top_barbers = list(
        Appointment.objects.values('barber__display_name')
        .annotate(bookings=Count('id')).order_by('-bookings')[:5]
    )
    top_services = list(
        Appointment.objects.values('service__name', 'service__category')
        .annotate(bookings=Count('id')).order_by('-bookings')[:5]
    )
    return Response({
        'totals': {
            'appointments': total,
            'pending': pending,
            'confirmed': confirmed,
            'cancelled': cancelled,
            'completed': completed,
            'revenue': float(revenue),
            'barbers': Barber.objects.count(),
            'services': Service.objects.count(),
            'today_appointments': today_count,
        },
        'top_barbers': top_barbers,
        'top_services': top_services,
    })


# ----- Public availability / slot generation -----

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def barber_busy_slots(request, pk):
    """Existing pending+confirmed appointments for a barber on a date.
    Used by the UI to grey-out the time picker."""
    d = request.query_params.get('date')
    if not d:
        return Response({'detail': 'date query param required.'}, status=400)
    qs = Appointment.objects.filter(
        barber_id=pk, appointment_date=d,
        status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED],
    ).values('id', 'start_time', 'end_time', 'status', 'service__name')
    return Response(list(qs))


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def barber_available_slots(request, pk):
    """Returns the list of 15-minute candidate slots for a given barber/service/date,
    each marked available/unavailable.
    Query: ?date=YYYY-MM-DD&service=<id>
    """
    try:
        barber = Barber.objects.get(pk=pk)
    except Barber.DoesNotExist:
        return Response({'detail': 'Barber not found.'}, status=404)

    d_param = request.query_params.get('date')
    s_param = request.query_params.get('service')
    if not (d_param and s_param):
        return Response({'detail': 'date and service query params required.'}, status=400)

    try:
        d = datetime.strptime(d_param, '%Y-%m-%d').date()
        service = Service.objects.get(pk=s_param)
    except (ValueError, Service.DoesNotExist):
        return Response({'detail': 'Invalid date or service.'}, status=400)

    if not barber.works_on(d):
        return Response({'date': d_param, 'works_on_this_day': False, 'slots': []})

    # Build candidate starts every 15 min from work_start to (work_end - duration)
    duration = timedelta(minutes=service.duration_minutes)
    day_start = datetime.combine(d, barber.work_start)
    day_end = datetime.combine(d, barber.work_end)
    latest_start = day_end - duration

    existing = list(Appointment.objects.filter(
        barber=barber, appointment_date=d,
        status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED],
    ).values_list('start_time', 'end_time'))

    now_naive = datetime.utcnow()
    slots = []
    cur = day_start
    while cur <= latest_start:
        slot_start = cur.time()
        slot_end = (cur + duration).time()
        # past?
        is_past = (datetime.combine(d, slot_start) < now_naive)
        # overlap with existing
        conflict = any(es < slot_end and ee > slot_start for es, ee in existing)
        slots.append({
            'start': slot_start.strftime('%H:%M'),
            'end': slot_end.strftime('%H:%M'),
            'available': (not is_past) and (not conflict),
        })
        cur += timedelta(minutes=15)

    return Response({
        'date': d_param,
        'works_on_this_day': True,
        'work_start': barber.work_start.strftime('%H:%M'),
        'work_end': barber.work_end.strftime('%H:%M'),
        'duration_minutes': service.duration_minutes,
        'slots': slots,
    })
