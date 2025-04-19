from rest_framework import permissions


class IsStaff(permissions.BasePermission):
    "Allow Access to Staff Only"

    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    "Allow Access to admins Only"

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.role == "admin":
            return True
        return False
    # def has_object_permission(self, request, view, obj):


class IsAuthorOrNot(permissions.BasePermission):
    "Allow Access to Author Only"

    def has_permission(self, request, view):
        user = request.user
        role = request.user.role
        is_true = (role == "author")
        return is_true
