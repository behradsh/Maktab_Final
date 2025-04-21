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


class IsCustomerOrNot(permissions.BasePermission):
    "Allow Access to Customers Only"

    def has_permission(self, request, view):
        flag = request.user.is_customer
        if flag:
            return flag
        return False

class IsSellerOrNot(permissions.BasePermission):
    "Allow Access to Sellers Only"
    def has_permission(self, request, view):
        flag = request.user.is_customer
        if not flag:
            return True
        return False

class IsSellerOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name="SellerOwners").exists()

class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name="Customers").exists()


class IsSellerManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name="SellerManagers").exists()

class IsSellerOperator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name="SellerOperators").exists()



class IsSelfOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.is_staff

class IsStoreOwnerOrManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name__in=["SellerOwners", "SellerManagers"]).exists()


class IsSellerOwnerOrEmployee(permissions.BasePermission):
    def has_permission(self, request, view):
        is_owner = request.user.groups.filter(name='SellerOwners').exists()
        is_employee = hasattr(request.user, 'user_store')
        return is_owner or is_employee
