from rest_framework.permissions import BasePermission


class IsStaffUser(BasePermission):
    """
    Grants access exclusively to authenticated users with is_staff=True.

    This is the single permission gate for every admin_panel endpoint.
    Regular creator accounts (is_staff=False) receive 403 Forbidden.
    Unauthenticated requests receive 401 Unauthorized via the JWT authenticator.
    """

    message = "You do not have permission to access the admin panel."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )
