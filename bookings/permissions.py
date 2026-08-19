from rest_framework import permissions


class IsOwnerBarberOrAdmin(permissions.BasePermission):
    """Customer (owner), the assigned barber, or admin can view/modify."""

    def has_object_permission(self, request, view, obj):
        u = request.user
        if not u or not u.is_authenticated:
            return False
        if getattr(u, 'is_admin_role', False) or u.is_staff:
            return True
        if obj.customer_id == u.id:
            return True
        # Barber assigned to this appointment
        if getattr(u, 'is_barber_role', False) and obj.barber.user_id == u.id:
            return True
        return False


class IsAdminUserRole(permissions.BasePermission):
    def has_permission(self, request, view):
        u = request.user
        if not u or not u.is_authenticated:
            return False
        return getattr(u, 'is_admin_role', False) or u.is_staff
