# from django.core.management.base import BaseCommand
# from django.contrib.auth.models import Group,Permission
# from django.contrib.contenttypes.models import ContentType
# from users_app.models import CustomUser
# from store_app.models import Store,StoreEmployee
# from products_app.models import Product
# from orders_app.models import Orders,OrderItems
# from django.utils.translation import gettext_lazy as _
# class Command(BaseCommand):
#     help = 'create necessary groups and permissions'
#
#     def handle(self, *args, **kwargs):
#         # Create groups
#         admin_group, created = Group.objects.get_or_create(name='Admins')
#         customer_group, created = Group.objects.get_or_create(name='Customers')
#         seller_owner_group, created = Group.objects.get_or_create(name='SellerOwners')
#         seller_manager_group, created = Group.objects.get_or_create(name='SellerManagers')
#         seller_operator_group, created = Group.objects.get_or_create(name='SellerOperators')
#
#         # Define permissions
#         content_types = ContentType.objects.get_for_models(CustomUser, Store,StoreEmployee ,Product, Orders,OrderItems)
#         # Clear existing permissions to avoid duplication
#         admin_group.permissions.clear()
#         customer_group.permissions.clear()
#         seller_owner_group.permissions.clear()
#         seller_manager_group.permissions.clear()
#         seller_operator_group.permissions.clear()
#         # Admins - Full access to everything
#         for content_type in content_types.values():
#             permissions = Permission.objects.filter(content_type=content_type)
#             for perm in permissions:
#                 admin_group.permissions.add(perm)
#
#         # Customers - Can only view products and manage their own orders
#         product_ct = content_types[Product]
#         order_ct = content_types[Orders]
#         customer_group.permissions.add(
#             Permission.objects.get(codename='view_product',
#                                    content_type=product_ct),
#             Permission.objects.get(codename='add_order',
#                                    content_type=order_ct),
#             Permission.objects.get(codename='view_order',content_type=order_ct),
#         )
#
#         # Seller Owners - Complete access to their stores, products, and orders
#         store_ct = content_types[Store]
#         employee_ct = content_types[StoreEmployee]
#         for codename in ['add','change','delete','view']:
#             seller_owner_group.permissions.add(
#                 Permission.objects.get(codename=f'{codename}_store',
#                                        content_type=store_ct),
#                 Permission.objects.get(codename=f'{codename}_product',
#                                        content_type=store_ct),
#                 Permission.objects.get(codename=f'{codename}_storeemployee',
#                                        content_type=employee_ct)
#             )
#             seller_owner_group.permissions.add(
#                 Permission.objects.get(codename='view_order',
#                                        content_type=order_ct),
#                 Permission.objects.get(codename='change_order',
#                                        content_type=order_ct)
#             )
#
#
#         # Seller Managers - Can manage products and view/update orders
#         for codename in ['add','change','delete','view']:
#             seller_manager_group.permissions.add(
#                 Permission.objects.get(codename=f'{codename}_product',
#                                        content_type=product_ct),
#             )
#         seller_manager_group.permissions.add(
#             Permission.objects.get(codename='view_store',
#                                    content_type=store_ct),
#             Permission.objects.get(codename='view_order',
#                                    content_type=order_ct),
#             Permission.objects.get(codename='change_order',
#                                    content_type=order_ct),
#         )
#         # Seller Operators - Read-only access to store, products, and orders
#         seller_operator_group.permissions.add(
#             Permission.objects.get(codename='view_store',
#                                    content_type=store_ct),
#             Permission.objects.get(codename='view_product',
#                                    content_type=product_ct),
#             Permission.objects.get(codename='view_order',
#                                    content_type=order_ct)
#         )











        # permissions = {
        #     'Admins': [
        #         Permission.objects.get(codename=codename, content_type=ct)
        #         for ct in content_types.values()
        #         for codename in ['add_%s' % ct.model, 'change_%s' % ct.model, 'delete_%s' % ct.model, 'view_%s' % ct.model]
        #     ],
        #     'Customers': [
        #         Permission.objects.get(codename='view_product', content_type=content_types[Product]),
        #         Permission.objects.get(codename='view_order', content_type=content_types[Orders]),
        #         Permission.objects.get(codename='add_order', content_type=content_types[Orders]),
        #         Permission.objects.get(codename='edit_order', content_type=content_types[Orders]),
        #         # Add more as needed
        #     ],
        #     'Seller Owners': [
        #         Permission.objects.get(codename=codename, content_type=content_types[Store])
        #         for codename in ['add_store', 'change_store', 'delete_store']
        #     ] + [
        #         Permission.objects.get(codename=codename, content_type=content_types[Product])
        #         for codename in ['add_product', 'change_product', 'delete_product']
        #     ] + [
        #         Permission.objects.get(codename=codename, content_type=content_types[Orders])
        #         for codename in ['view_order', 'change_order']
        #     ],
        #     'Seller Managers': [
        #         Permission.objects.get(codename=codename, content_type=content_types[Product])
        #         for codename in ['add_product', 'change_product', 'delete_product']
        #     ] + [
        #         Permission.objects.get(codename=codename, content_type=content_types[Orders])
        #         for codename in ['view_order', 'change_order']
        #     ],
        #     'Seller Operators': [
        #         Permission.objects.get(codename='view_product', content_type=content_types[Product]),
        #         Permission.objects.get(codename='view_order', content_type=content_types[Orders]),
        #     ],
        # }
        #
        # # Assign permissions to groups
        # admin_group.permissions.set(permissions['Admins'])
        # customer_group.permissions.set(permissions['Customers'])
        # seller_owner_group.permissions.set(permissions['Seller Owners'])
        # seller_manager_group.permissions.set(permissions['Seller Managers'])
        # seller_operator_group.permissions.set(permissions['Seller Operators'])
        #
        # self.stdout.write(self.style.SUCCESS('Groups and permissions set up successfully'))