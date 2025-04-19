from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from products_app.models import Product, Comment
from store_app.models import Store, StoreEmployee
from orders_app.models import Orders, OrderItems
from users_app.models import CustomUser, Address


@receiver(post_migrate)
def create_user_groups(sender, **kwargs):
    # Define your groups
    groups = {
        "Admins": [],
        "Customers": [
            (Product, ['view']),
            (Orders, ['add', 'view', 'change', 'delete']),
            (OrderItems, ['add', 'view', 'change', 'delete']),
            (Address, ['add', 'view', 'change', 'delete']),
            (CustomUser, ['view', 'change']),
            (Comment, ['add', 'view', 'change', 'delete']),
        ],
        "SellerOwners": [
            (Store, ['add', 'view', 'change', 'delete']),
            (StoreEmployee, ['add', 'view', 'change', 'delete']),
            (Product, ['add', 'view', 'change', 'delete']),
            (Orders, ['view', 'change']),
            (OrderItems, ['view', 'change']),
            (Comment, ['view', 'change']),
        ],
        "SellerManagers": [
            (Product, ['add', 'view', 'change', 'delete']),
            (Orders, ['view', 'change']),
            (Comment, ['view', 'change']),
        ],
        "SellerOperators": [
            (Store, ['view']),
            (Product, ['view']),
            (Orders, ['view']),
            (OrderItems, ['view']),
            (Comment, ['view']),
        ],
    }

    for group_name, perms in groups.items():
        group, _ = Group.objects.get_or_create(name=group_name)
        for model, actions in perms:
            content_type = ContentType.objects.get_for_model(model)
            for action in actions:
                codename = f"{action}_{model._meta.model_name}"
                try:
                    permission = Permission.objects.get(codename=codename, content_type=content_type)
                    group.permissions.add(permission)
                except Permission.DoesNotExist:
                    print(f"Permission {codename} not found")

# Admins get all permissions
admins, _ = Group.objects.get_or_create(name="Admins")
admins.permissions.set(Permission.objects.all())
