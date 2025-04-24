from itertools import count

from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
import random
from rest_framework import (generics, status, views, permissions, viewsets)
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser, Address
from products_app.models import Product
from products_app.serializers import ProductSerializer
from orders_app.models import Orders, OrderItems, Cart, CartItem
from rest_framework.views import APIView
from .serializers import (UserRegisterSerializer,
                          SellerRegisterSerializer,
                          LoginOTPRequestSerializer,
                          VerifyOTPSerializer,
                          LogOutSerializer,
                          UserDetailSerializer,
                          ChangePasswordSerializer,
                          PhoneLoginRequestSerializer,
                          PhoneVerifyOTPSerializer,
                          AddressSerializer,
                          CustomerProfileSerializer,
                          SellerProfileSerializer,
                          SellerChangePasswordSerializer, )
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils.translation import gettext_lazy as _
from .tasks import (send_otp_email, send_sms_otp)
from core_app.custom_permissions import *
from orders_app.serializers import OrderSerializer
from store_app.models import Store, StoreEmployee
from store_app.serializers import StoreSerializer, StoreEmployeeCreateSerializer
from users_app.serializers import CustomerProfileSerializer


# Create your views here.
def get_session_cart(request):
    if 'cart' not in request.session:
        request.session['cart'] = {}  # {product_id: quantity}
    return request.session['cart']


# get user cart
def get_user_cart(user):
    cart, created = Cart.objects.get_or_create(user=user)
    return cart


class CustomerRegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.filter(is_customer=True)
    permission_classes = (AllowAny,)
    serializer_class = UserRegisterSerializer


class SellerRegisterView(generics.CreateAPIView):
    serializer_class = SellerRegisterSerializer
    queryset = CustomUser.objects.filter(is_customer=False)
    permission_classes = (AllowAny,)

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # check old password
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({"old password": ["Wrong password"]},
                                status=status.HTTP_400_BAD_REQUEST)
            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message": ["Your password has been Changed"]}, )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogOutAPIView(APIView):
    serializer_class = LogOutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # serializer.save()
        logout(request)
        return Response("Successfully LoggedOut", status=status.HTTP_204_NO_CONTENT)


# Implementing the OTP for sending mail
def generate_random_digits(n=6):
    return "".join(map(str, random.sample(range(0, 10), n)))


class LoginOTPView(APIView):
    """
    Handle initial login authentication and OTP generation
    """
    permission_classes = [AllowAny]
    serializer_class = LoginOTPRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        # Get the authenticated user from the serializer
        user = serializer.user
        email = serializer.validated_data['email']

        try:
            # Generate a 6-digit code and set the expiry time to 1 hour from now
            verification_code = generate_random_digits()
            user.otp = verification_code
            user.otp_expiry_time = timezone.now() + timedelta(hours=1)
            user.save()

            # Send the code via email
            send_otp_email.delay(email, verification_code)

            return Response({
                'detail': 'Verification code sent successfully.',
                'email': email,
                'redirect_url': '/api/login/verify/'  # Instruct frontend to redirect
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'detail': f'Failed to generate OTP: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyOTPView(APIView):
    """
    Verify OTP and issue JWT tokens
    """
    permission_classes = [AllowAny]
    serializer_class = VerifyOTPSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # OTP validation happened in the serializer
        email = serializer.validated_data['email']

        try:
            user = CustomUser.objects.get(email=email)

            # Reset OTP after successful verification
            user.otp = None
            user.otp_expiry_time = None
            user.save()
            # Merge session cart with user cart
            if 'cart' in request.session:
                session_cart = request.session['cart']
                user_cart = get_user_cart(user)
                for product_id, quantity in session_cart.items():
                    try:
                        product = Product.objects.get(id=product_id)
                        cart_item, created = CartItem.objects.get_or_create(
                            cart=user_cart,
                            product=product,
                            defaults={'quantity': quantity}
                        )
                        if not created:
                            cart_item.quantity += quantity
                            cart_item.save()
                    except Product.DoesNotExist:
                        continue
                del request.session['cart']
                request.session.modified = True
                serializer = CustomerProfileSerializer(user)
            # Return the token and user data
            return Response(serializer.data, status=status.HTTP_200_OK)


        except CustomUser.DoesNotExist:
            return Response({
                'detail': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                'detail': f'Verification failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            verification_code = generate_random_digits()
            user.otp = verification_code
            user.otp_expiry_time = timezone.now() + timedelta(hours=1)
            user.save()
            send_otp_email.delay(email, verification_code)
            return Response({
                'detail': 'Verification code resent successfully.',
                'email': email
            }, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({
                'detail': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)


class PhoneLoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PhoneLoginRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.user
        phone = serializer.validated_data['phone']

        try:
            verification_code = generate_random_digits()
            user.otp = verification_code
            user.otp_expiry_time = timezone.now() + timedelta(minutes=10)
            user.save()

            send_sms_otp.delay(phone, verification_code)

            return Response({
                'detail': 'SMS sent to phone.',
                'phone': phone,
                'redirect_url': 'login/phone/verify/'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'detail': f'Failed to send OTP: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PhoneVerifyOTPView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PhoneVerifyOTPSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['phone']

        try:
            user = CustomUser.objects.get(phone=phone)
            user.otp = None
            user.otp_expiry_time = None
            user.save()
            # Merge session cart with user cart
            if 'cart' in request.session:
                session_cart = request.session['cart']
                user_cart = get_user_cart(user)
                for product_id, quantity in session_cart.items():
                    try:
                        product = Product.objects.get(id=product_id)
                        cart_item, created = CartItem.objects.get_or_create(
                            cart=user_cart,
                            product=product,
                            defaults={'quantity': quantity}
                        )
                        if not created:
                            cart_item.quantity += quantity
                            cart_item.save()
                    except Product.DoesNotExist:
                        continue
                del request.session['cart']
                request.session.modified = True

            return Response(serializer.data, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response({
                'detail': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'detail': f'Verification failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = CustomerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = CustomUser
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({'old_password': 'Wrong password.'}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'status': 'password set'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerAddressView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    model = Address
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return Address.objects.filter(customer=user)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(customer=user)


class CustomerAddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Address.objects.filter(customer=self.request.user)

    # Optional: Add this method to ensure users can only modify their own addresses
    def check_object_permissions(self, request, obj):
        if obj.customer != request.user:
            self.permission_denied(request, message="You don't have permission to access this address.")
        return super().check_object_permissions(request, obj)

    def perform_update(self, serializer):
        # If this address is being set as default, unset any existing default
        if serializer.validated_data.get('is_default', False):
            Address.objects.filter(
                customer=self.request.user,
                is_default=True
            ).exclude(pk=self.get_object().pk).update(is_default=False)
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()
        return "Address deleted."


# class CustomerPanelViewSet(viewsets.ModelViewSet):
#     permission_classes = [IsCustomerOrNot]
#     serializer_class = CustomerProfileSerializer
#
#     def get_queryset(self):
#         # Restrict to the authenticated user
#         return CustomUser.objects.filter(id=self.request.user.id)
#
#     def get_object(self):
#         # Always return the authenticated user
#         return self.request.user
#
#     @action(detail=False, methods=['get'], url_path='address')
#     def list_addresses(self, request):
#         addresses = request.user.addresses.all()
#         serializer = AddressSerializer(addresses, many=True)
#         return Response(serializer.data)
#
#     @action(detail=False, methods=['post'], url_path='address')
#     def create_address(self, request):
#         serializer = AddressSerializer(data=request.data, context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         serializer.save(user=request.user)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#     @action(detail=False, methods=['patch','put'], url_path='address/(?P<address_id>[^/.]+)')
#     def update_address(self, request, address_id=None):
#         try:
#             address = request.user.addresses.get(id=address_id)
#         except Address.DoesNotExist:
#             return Response({'detail': 'Address not found'}, status=status.HTTP_404_NOT_FOUND)
#         serializer = AddressSerializer(address, data=request.data, partial=True, context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
#
#     @action(detail=False, methods=['delete'], url_path='address/(?P<address_id>[^/.]+)')
#     def delete_address(self, request, address_id=None):
#         try:
#             address = request.user.addresses.get(id=address_id)
#         except Address.DoesNotExist:
#             return Response({'detail': 'Address not found'}, status=status.HTTP_404_NOT_FOUND)
#         address.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
#
#     @action(detail=False, methods=['get'], url_path='orders')
#     def list_orders(self, request):
#         orders = request.user.orders.all()
#         serializer = OrderSerializer(orders, many=True)
#         return Response(serializer.data)

class SellerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = SellerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
    # serializer_class = SellerProfileSerializer
    # permission_classes = [permissions.IsAuthenticated, IsSellerOrNot]
    #
    # def get_object(self):
    #     return self.request.user

    # def retrieve(self, request, *args, **kwargs):
    #     user = self.get_object()
    #     return Response({
    #         'id': user.id,
    #         'username': user.username,
    #         'email': user.email,
    #         'phone': str(user.phone),
    #         'gender': user.gender,
    #         'profile_img': user.profile_img.url if user.profile_img else None
    #     })


class SellerChangePasswordView(generics.UpdateAPIView):
    serializer_class = SellerChangePasswordSerializer
    model = CustomUser
    permission_classes = (IsAuthenticated, IsSellerOrNot)

    def update(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({'old_password': 'Wrong password.'}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'status': 'password set'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HomeView(generics.ListAPIView):
    permission_classes = []

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context



def get_user_store(user):
    if user.groups.filter(name='SellerOwners').exists():
        try:
            return user.store  # Using the related_name="store" from Store model
        except Store.DoesNotExist:
            raise Exception('Store not found')
    try:
        # Access through the user_store related_name from StoreEmployee model
        employee = user.user_store
        # Return the store using store_id field (ForeignKey to Store)
        return employee.store_id
    except StoreEmployee.DoesNotExist:
        raise Exception('Not assigned to a store')


class SellerProductListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsSellerOrNot, IsSellerOwner, IsSellerManager]
    serializer_class = ProductSerializer

    def get_queryset(self):
        store = get_user_store(self.request.user)
        return store.products.all()

    def perform_create(self, serializer):
        if self.request.user.groups.filter(name='SellerOperators').exists():
            raise Exception('Operators cannot create products')
        store = get_user_store(self.request.user)
        serializer.save(store=store)


class SellerProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsSellerOrNot, IsSellerOwner, IsSellerManager]
    serializer_class = ProductSerializer

    def get_queryset(self):
        store = get_user_store(self.request.user)
        return store.products.all()

    def perform_update(self, serializer):
        if self.request.user.groups.filter(name='SellerOperators').exists():
            raise Exception('Operators cannot update products')
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user.groups.filter(name='SellerOperators').exists():
            raise Exception('Operators cannot delete products')
        instance.delete()


class SellerOrderListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsSellerOrNot, IsSellerOwner, IsSellerManager]
    serializer_class = OrderSerializer

    def get_queryset(self):
        store = self.get_user_store(self.request.user)
        return Orders.objects.filter(store=store).select_related(
            'customer', 'store'
        ).prefetch_related(
            'orderitems_set__product'
        ).order_by('-created_at')

    def get_user_store(self, user):
        if hasattr(user, 'user_store'):
            return user.user_store.store_id
        elif hasattr(user, 'store'):
            return user.store
        raise Exception("User is not associated with any store")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class SellerOrderUpdateView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsSellerOrNot, IsSellerOwner, IsSellerManager]
    serializer_class = OrderSerializer

    def get_queryset(self):
        store = self.get_user_store(self.request.user)
        return Orders.objects.filter(store=store).select_related(
            'customer', 'store'
        ).prefetch_related(
            'orderitems_set__product'
        ).order_by('-created_at')

    def get_user_store(self, user):
        if hasattr(user, 'user_store'):
            return user.user_store.store_id
        elif hasattr(user, 'store'):
            return user.store
        raise Exception("User is not associated with any store")

    def perform_update(self, serializer):
        if self.request.user.groups.filter(name='SellerOperators').exists():
            raise Exception('Operators cannot update orders')
        serializer.save()


class SellerEmployeeListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsSellerOrNot, IsSellerOwner, ]
    serializer_class = StoreEmployeeCreateSerializer

    def get_queryset(self):
        store = get_user_store(self.request.user)
        return store.employees.all()

    def perform_create(self, serializer):
        store = get_user_store(self.request.user)
        serializer.save(store=store)


class SellerEmployeeRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsStoreOwnerOrManager]
    serializer_class = StoreEmployeeCreateSerializer

    def get_queryset(self):
        store = self.get_user_store(self.request.user)
        return StoreEmployee.objects.filter(store_id=store).select_related('user_id')

    def get_user_store(self, user):
        if hasattr(user, 'store'):
            return user.store
        raise Exception("User is not a store owner")

    def perform_update(self, serializer):
        # Prevent changing store association
        if 'store_id' in serializer.validated_data:
            raise Exception("Cannot change store employee")
        serializer.save()

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_manager:
            # Ensure at least one manager remains
            managers_count = StoreEmployee.objects.filter(
                store_id=instance.store_id,
                is_manager=True
            ).count()
            if managers_count <= 1:
                return Response(
                    {"detail": "Cannot delete the last manager"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return super().delete(request, *args, **kwargs)


class SellerReportsView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, IsSellerOrNot, IsSellerOwner]

    def get(self, request, *args, **kwargs):
        try:
            store = self.get_user_store(request.user)
            time_filter = request.query_params.get('time_filter', 'all')
            orders = store.orders.all()

            # Apply time filter if specified
            if time_filter != 'all':
                time_filters = {
                    'daily': 1,
                    'weekly': 7,
                    'monthly': 30,
                    'quarterly': 90,
                    'yearly': 365
                }
                if time_filter in time_filters:
                    start_date = timezone.now() - timedelta(days=time_filters[time_filter])
                    orders = orders.filter(created_at__gte=start_date)
                else:
                    raise ValueError("Invalid time filter")

            # Calculate total sales
            sales_agg = orders.aggregate(
                total_orders=count('id'),
                total_revenue=sum('total_amount')
            )

            # Get best selling products
            best_selling = OrderItems.objects.filter(
                order__store=store,
                order__created_at__gte=start_date if time_filter != 'all' else None
            ).values(
                'product__id',
                'product__name'
            ).annotate(
                total_quantity=sum('quantity'),
                total_sales=sum('price')
            ).order_by('-total_quantity')[:5]

            # Get order status distribution
            status_distribution = orders.values('status').annotate(
                count=count('id')
            ).order_by('-count')

            return Response({
                'time_period': time_filter,
                'total_orders': sales_agg['total_orders'],
                'total_revenue': float(sales_agg['total_revenue'] or 0),
                'best_selling_products': list(best_selling),
                'order_status_distribution': list(status_distribution)
            })

        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def get_user_store(self, user):
        if hasattr(user, 'store'):
            return user.store
        raise Exception("User is not a store owner")
