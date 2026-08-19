"""Service catalog + Barber roster."""
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Service(models.Model):
    """A bookable service like 'Classic Haircut' or 'Beard Trim'."""
    class Category(models.TextChoices):
        HAIRCUT = 'haircut', 'Haircut'
        BEARD = 'beard', 'Beard'
        SHAVE = 'shave', 'Shave'
        COMBO = 'combo', 'Haircut + Beard'
        KIDS = 'kids', 'Kids'
        STYLING = 'styling', 'Styling & Wash'

    name = models.CharField(max_length=120)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.HAIRCUT)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    price = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])
    duration_minutes = models.PositiveIntegerField(default=30, help_text="Service length in minutes")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} · {self.duration_minutes}min · ${self.price}"


class Barber(models.Model):
    """A barber on staff. Optionally linked to a User account."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='barber_profile',
    )
    display_name = models.CharField(max_length=120)
    bio = models.TextField(blank=True)
    avatar_url = models.URLField(blank=True)
    specialty = models.CharField(max_length=120, blank=True, help_text="e.g. Fades, Beard sculpting")
    years_experience = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)

    # Working hours (per-day; same window every day for simplicity).
    work_start = models.TimeField(default='09:00')
    work_end = models.TimeField(default='19:00')

    # Days off (Python weekday integers: 0=Mon .. 6=Sun). Stored as CSV.
    days_off = models.CharField(max_length=20, blank=True,
                                help_text="Comma-separated weekday numbers (0=Mon … 6=Sun)")

    services = models.ManyToManyField(Service, related_name='barbers', blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_name']

    def __str__(self):
        return self.display_name

    def days_off_list(self):
        if not self.days_off:
            return []
        try:
            return [int(x.strip()) for x in self.days_off.split(',') if x.strip() != '']
        except ValueError:
            return []

    def works_on(self, date) -> bool:
        return date.weekday() not in self.days_off_list()
