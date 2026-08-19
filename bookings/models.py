"""Appointment models with conflict-prevention business logic."""
from decimal import Decimal
from datetime import datetime, timedelta, time

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from services.models import Service, Barber


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        REJECTED = 'rejected', 'Rejected'
        CANCELLED = 'cancelled', 'Cancelled'
        COMPLETED = 'completed', 'Completed'
        NO_SHOW = 'no_show', 'No-show'

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='appointments')
    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name='appointments')

    appointment_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(blank=True, null=True)  # auto-derived from service.duration_minutes

    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-appointment_date', '-start_time']
        indexes = [
            models.Index(fields=['barber', 'appointment_date']),
            models.Index(fields=['customer', 'appointment_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return (f"{self.barber.display_name} | {self.customer.username} | "
                f"{self.service.name} | {self.appointment_date} {self.start_time}")

    # --- derived ---

    def compute_end_time(self) -> time:
        """end = start + service.duration_minutes (capped at 23:59)."""
        if not (self.start_time and self.service_id):
            return None
        start_dt = datetime.combine(self.appointment_date or datetime.utcnow().date(), self.start_time)
        end_dt = start_dt + timedelta(minutes=self.service.duration_minutes)
        # Don't allow rolling over to next day
        if end_dt.date() != start_dt.date():
            return time(23, 59)
        return end_dt.time()

    @property
    def duration_minutes(self) -> int:
        return self.service.duration_minutes if self.service_id else 0

    # --- validation ---

    BLOCKING_STATUSES = ('pending', 'confirmed')

    def overlaps_with_existing(self) -> bool:
        """One barber cannot have two overlapping active bookings."""
        if not (self.barber_id and self.appointment_date and self.start_time and self.end_time):
            return False
        qs = Appointment.objects.filter(
            barber_id=self.barber_id,
            appointment_date=self.appointment_date,
            status__in=self.BLOCKING_STATUSES,
        )
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        # Standard interval overlap: existing.start < new.end AND existing.end > new.start
        qs = qs.filter(start_time__lt=self.end_time, end_time__gt=self.start_time)
        return qs.exists()

    def clean(self):
        errors = {}

        # 1. Required relations
        if not self.barber_id or not self.service_id:
            return

        # 2. Service must be active
        if not self.service.is_active:
            errors['service'] = 'This service is currently unavailable.'

        # 3. Barber must be active
        if not self.barber.is_active:
            errors['barber'] = 'This barber is not accepting appointments.'

        # 4. Barber must offer the service
        if not self.barber.services.filter(pk=self.service_id).exists():
            errors['service'] = f'{self.barber.display_name} does not offer this service.'

        # 5. Compute end_time
        if self.start_time and self.appointment_date:
            self.end_time = self.compute_end_time()

        # 6. Must not be in the past (use 5-minute grace for clock skew)
        if self.appointment_date and self.start_time:
            booking_dt = datetime.combine(self.appointment_date, self.start_time)
            now_naive = datetime.utcnow()
            if booking_dt < now_naive - timedelta(minutes=5):
                errors['appointment_date'] = 'Cannot book a slot in the past.'

        # 7. Barber must work that weekday
        if self.appointment_date and not self.barber.works_on(self.appointment_date):
            errors['appointment_date'] = f'{self.barber.display_name} is off on this day.'

        # 8. Start & end must fit within barber's working hours
        if self.start_time and self.end_time:
            if self.start_time < self.barber.work_start:
                errors['start_time'] = (
                    f"{self.barber.display_name} starts at {self.barber.work_start.strftime('%H:%M')}.")
            if self.end_time > self.barber.work_end:
                errors['start_time'] = (
                    f"This appointment would end after {self.barber.display_name}'s "
                    f"closing time ({self.barber.work_end.strftime('%H:%M')}).")

        # 9. Overlap with another booking of the same barber
        if self.start_time and self.end_time and self.status in self.BLOCKING_STATUSES:
            if self.overlaps_with_existing():
                errors['start_time'] = 'This barber is already booked during that time slot.'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.service_id and self.start_time and self.appointment_date:
            self.end_time = self.compute_end_time()
            self.total_price = self.service.price
        self.full_clean()
        super().save(*args, **kwargs)
