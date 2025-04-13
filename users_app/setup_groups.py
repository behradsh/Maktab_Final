from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group,Permission
from django.contrib.contenttypes.models import ContentType
from users_app.models import CustomUser
from store_app.models import Store
from products_app.models import Product
from orders_app.models import Orders
from django.utils.translation import gettext_lazy as _
class Command(BaseCommand):
    help = 'Set up groups and permissions'

    def handle(self, *args, **kwargs):
        # Create groups
        admin_group, _ = Group.objects.get_or_create(name='Admins')
        customer_group, _ = Group.objects.get_or_create(name='Customers')
        seller_owner_group, _ = Group.objects.get_or_create(name='Seller Owners')
        seller_manager_group, _ = Group.objects.get_or_create(name='Seller Managers')
        seller_operator_group, _ = Group.objects.get_or_create(name='Seller Operators')

        # Define permissions
        content_types = ContentType.objects.get_for_models(CustomUser, Store, Product, Orders)
        permissions = {
            'Admins': [
                Permission.objects.get(codename=codename, content_type=ct)
                for ct in content_types.values()
                for codename in ['add_%s' % ct.model, 'change_%s' % ct.model, 'delete_%s' % ct.model, 'view_%s' % ct.model]
            ],
            'Customers': [
                Permission.objects.get(codename='view_product', content_type=content_types[Product]),
                Permission.objects.get(codename='view_order', content_type=content_types[Orders]),
                Permission.objects.get(codename='add_order', content_type=content_types[Orders]),
                Permission.objects.get(codename='edit_order', content_type=content_types[Orders]),
                # Add more as needed
            ],
            'Seller Owners': [
                Permission.objects.get(codename=codename, content_type=content_types[Store])
                for codename in ['add_store', 'change_store', 'delete_store']
            ] + [
                Permission.objects.get(codename=codename, content_type=content_types[Product])
                for codename in ['add_product', 'change_product', 'delete_product']
            ] + [
                Permission.objects.get(codename=codename, content_type=content_types[Orders])
                for codename in ['view_order', 'change_order']
            ],
            'Seller Managers': [
                Permission.objects.get(codename=codename, content_type=content_types[Product])
                for codename in ['add_product', 'change_product', 'delete_product']
            ] + [
                Permission.objects.get(codename=codename, content_type=content_types[Orders])
                for codename in ['view_order', 'change_order']
            ],
            'Seller Operators': [
                Permission.objects.get(codename='view_product', content_type=content_types[Product]),
                Permission.objects.get(codename='view_order', content_type=content_types[Orders]),
            ],
        }

        # Assign permissions to groups
        admin_group.permissions.set(permissions['Admins'])
        customer_group.permissions.set(permissions['Customers'])
        seller_owner_group.permissions.set(permissions['Seller Owners'])
        seller_manager_group.permissions.set(permissions['Seller Managers'])
        seller_operator_group.permissions.set(permissions['Seller Operators'])

        self.stdout.write(self.style.SUCCESS('Groups and permissions set up successfully'))