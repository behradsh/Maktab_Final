from rest_framework import permissions
from orders_app.models import OrderItems


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

class HasPurchasedProduct(permissions.BasePermission):
    """
    Allow GET (listing existing comments) for everyone authenticated,
    but only allow POST if the user has at least one OrderItem
    referencing the product they’re commenting on.
    """

    def has_permission(self, request, view):
        # Allow any authenticated user to list comments
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return request.user and request.user.is_authenticated

        # For POST (creating), we need to check product ownership
        if request.method == 'POST':
            user = request.user
            if not user or not user.is_authenticated:
                return False

            # Expect the URL kwarg 'pk' for product ID, or
            # fall back to request.data['product']
            product_id = view.kwargs.get('pk') or request.data.get('product')
            if not product_id:
                return False

            # Check if the user has any order item for that product
            return OrderItems.objects.filter(
                order__customer=user,
                product_id=product_id
            ).exists()

        # Default deny
        return False