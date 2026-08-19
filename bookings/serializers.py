from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from services.serializers import ServiceSerializer, BarberSerializer
from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    customer_username = serializers.CharField(source='customer.username', read_only=True)
    barber_detail = BarberSerializer(source='barber', read_only=True)
    service_detail = ServiceSerializer(source='service', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    duration_minutes = serializers.IntegerField(read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'customer', 'customer_username',
            'barber', 'barber_detail',
            'service', 'service_detail',
            'appointment_date', 'start_time', 'end_time',
            'duration_minutes', 'total_price',
            'status', 'status_display', 'notes',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'customer', 'end_time', 'total_price',
                            'status', 'created_at', 'updated_at']

    def validate(self, attrs):
        instance = Appointment(
            customer=self.context['request'].user if self.instance is None else self.instance.customer,
            barber=attrs.get('barber', getattr(self.instance, 'barber', None)),
            service=attrs.get('service', getattr(self.instance, 'service', None)),
            appointment_date=attrs.get('appointment_date', getattr(self.instance, 'appointment_date', None)),
            start_time=attrs.get('start_time', getattr(self.instance, 'start_time', None)),
            status=getattr(self.instance, 'status', Appointment.Status.PENDING),
        )
        if self.instance:
            instance.pk = self.instance.pk
        try:
            instance.clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(
                e.message_dict if hasattr(e, 'message_dict') else {'detail': e.messages}
            )
        return attrs


class AdminStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['status']

    def validate_status(self, value):
        if value not in dict(Appointment.Status.choices):
            raise serializers.ValidationError("Invalid status.")
        return value
