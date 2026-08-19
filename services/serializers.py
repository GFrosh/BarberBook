from rest_framework import serializers
from .models import Service, Barber


class ServiceSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = Service
        fields = ['id', 'name', 'category', 'category_display', 'description', 'image_url',
                  'price', 'duration_minutes', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class BarberSerializer(serializers.ModelSerializer):
    services_detail = ServiceSerializer(source='services', many=True, read_only=True)
    service_ids = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(), many=True, write_only=True, source='services', required=False
    )
    days_off_list = serializers.SerializerMethodField()

    class Meta:
        model = Barber
        fields = ['id', 'display_name', 'bio', 'avatar_url', 'specialty',
                  'years_experience', 'rating',
                  'work_start', 'work_end', 'days_off', 'days_off_list',
                  'services_detail', 'service_ids', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at', 'rating']

    def get_days_off_list(self, obj):
        return obj.days_off_list()
