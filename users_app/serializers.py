import datetime

from rest_framework import serializers
from .models import CustomUser, Address
from store_app.models import Store
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import Group
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import (RefreshToken, AccessToken, TokenError)
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


# Serializers Customer Registration
class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True,
                                     validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password2', 'phone',
                  'first_name', 'last_name', 'gender']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
            'phone': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Passwords fields didnt match'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = CustomUser.objects.create(
            username=validated_data.get('username', ''),
            email=validated_data.get('email', ''),
            phone=validated_data.get('phone', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            gender=validated_data.get('gender', False),
            is_customer=validated_data.get('is_customer', True),
            is_staff=validated_data.get('is_staff', False),
        )
        user.set_password(validated_data.get('password', ''))
        user.save()
        try:
            group, _ = Group.objects.get_or_create(name='Customers')
            user.groups.add(group)
        except Group.DoesNotExist:
            group = None
        return user


# Serializers Seller Registration
class SellerRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True,
                                     validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    store_name = serializers.CharField(max_length=100, required=True, write_only=True)
    store_address = serializers.CharField(max_length=250, required=True, write_only=True)
    store_city = serializers.CharField(max_length=25, required=True, write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password2', 'phone',
                  'first_name', 'last_name', 'store_name', 'store_address', 'gender', 'store_city']
        extra_kwargs = {
            'username': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
            'phone': {'required': True},
            'store_name': {'required': False, },
            'store_address': {'required': False},
            'gender': {'required': True},
            'store_city': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Passwords fields didnt match'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = CustomUser.objects.create(
            username=validated_data.get('username', ''),
            email=validated_data.get('email', ''),
            phone=validated_data.get('phone', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            gender=validated_data.get('gender', False),
            is_customer=validated_data.get('is_customer', False),
            is_staff=validated_data.get('is_staff', False),
        )
        user.set_password(validated_data.get('password'))
        Store.objects.create(
            owner=user,
            name=validated_data.get('store_name'),
            address=validated_data.get('store_address'),
            city=validated_data.get('store_city'),
        )
        user.save()
        store = Store.objects.get(owner=user)
        self.store = store
        try:
            group, _ = Group.objects.get_or_create(name='SellerOwners')
            user.groups.add(group)
        except Group.DoesNotExist:
            group = None
        return user

    def to_representation(self, instance):
        # method to return store as response
        rep = super().to_representation(instance)
        store = getattr(self, 'store', None)
        if store:
            rep['store'] = {
                'id': store.id,
                'name': store.name,
                'address': store.address,
            }
        return rep

class LoginOTPRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        # Use authenticate with email
        user = authenticate(request=self.context.get('request'), email=email, password=password)
        if not user:
            raise serializers.ValidationError(_('Invalid credentials, try again'))
        if not user.is_active:
            raise serializers.ValidationError(_('Account disabled, contact admin'))

        # Store user for view
        self.user = user
        return {
            'email': user.email,
            'username': user.username,
            'token': user.token(),  # Assuming token() method works
            'user_type': user.is_customer,
        }


class VerifyOTPSerializer(serializers.Serializer):
    """Serializer for OTP verification"""
    email = serializers.EmailField()
    otp = serializers.CharField(
        min_length=6,
        max_length=6,
        write_only=True
    )
    token = serializers.SerializerMethodField()
    user_type = serializers.SerializerMethodField()
    redirect_url = serializers.SerializerMethodField()

    def get_token(self, obj):
        """Generate JWT tokens for the user"""
        user = CustomUser.objects.get(email=obj['email'])
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

    def get_user_type(self, obj):
        """Return the user type (customer or seller)"""
        user = CustomUser.objects.get(email=obj['email'])
        return 'customer' if user.is_customer else 'seller'

    def get_redirect_url(self, obj):
        """Return the appropriate redirect URL based on user type"""
        user = CustomUser.objects.get(email=obj['email'])
        if user.is_customer:
            return '/customer/dashboard/'  # Customer dashboard URL
        else:
            return '/seller/dashboard/'  # Seller dashboard URL

    def validate(self, attrs):
        """Validate the OTP"""
        email = attrs.get('email')
        otp = attrs.get('otp')

        try:
            user = CustomUser.objects.get(email=email)

            # Check if OTP is valid and not expired
            if not user.otp or user.otp != otp:
                raise serializers.ValidationError(_('Invalid verification code'))

            if not user.otp_expiry_time or user.otp_expiry_time < timezone.now():
                raise serializers.ValidationError(_('Verification code has expired'))

            # All validations passed, return the data
            return {
                'email': email,
                'otp_valid': True
            }

        except CustomUser.DoesNotExist:
            raise serializers.ValidationError(_('No user found with this email'))


class LogOutSerializer(serializers.ModelSerializer):
    """
    serializer for logout
    """
    refresh = serializers.CharField()

    class Meta:
        model = CustomUser
        fields = "__all__"

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')


class ChangePasswordSerializer(serializers.Serializer):
    """
    serializer for change password
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs


class UserDetailSerializer(serializers.ModelSerializer):
    """
    serializer for user detail
    """
    groups = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'phone', 'first_name', 'last_name',
                  'gender', 'is_customer', 'profile_img', 'groups')
        read_only_fields = ('id', 'groups','is_customer','username','email')


class PhoneLoginRequestSerializer(serializers.Serializer):
    """
    serializer for login with phone number
    """
    phone = serializers.CharField(required=True)

    def validate(self, attrs):
        phone = attrs.get('phone')
        try:
            user = CustomUser.objects.get(phone=phone)
            if not user.is_active:
                raise serializers.ValidationError(_('Account disabled, contact admin'))
            self.user = user
            return {'phone': phone}
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError(_('No user found with this phone number'))


class PhoneVerifyOTPSerializer(serializers.Serializer):
    """
    serializer for OTP verification
    """
    phone = serializers.CharField()
    otp = serializers.CharField(min_length=6, max_length=6, write_only=True)
    token = serializers.SerializerMethodField()
    user_type = serializers.SerializerMethodField()
    redirect_url = serializers.SerializerMethodField()

    def get_token(self, obj):
        user = CustomUser.objects.get(phone=obj['phone'])
        return user.token()

    def get_user_type(self, obj):
        user = CustomUser.objects.get(phone=obj['phone'])
        return 'customer' if user.is_customer else 'seller'

    def get_redirect_url(self, obj):
        user = CustomUser.objects.get(phone=obj['phone'])
        return '/customer/dashboard/' if user.is_customer else '/seller/dashboard/'

    def validate(self, attrs):
        phone = attrs.get('phone')
        otp = attrs.get('otp')

        try:
            user = CustomUser.objects.get(phone=phone)

            if not user.otp or user.otp != otp:
                raise serializers.ValidationError(_('Invalid verification code'))

            if not user.otp_expiry_time or user.otp_expiry_time < timezone.now():
                raise serializers.ValidationError(_('Verification code has expired'))

            return {
                'phone': phone,
                'otp_valid': True,
            }
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError(_('No user found with this phone number'))


class AddressSerializer(serializers.ModelSerializer):
    """
    serializer for user address
    """
    class Meta:
        model = Address
        fields = ['id', 'address_line', 'city', 'province', 'postal_code', 'country', 'is_default']

    def create(self, validated_data):
        is_default = validated_data.get('is_default', False)
        user = self.context['request'].user
        if is_default:
            Address.objects.filter(customer=user, is_default=True).update(is_default=False)
        return Address.objects.create(**validated_data)

class CustomerProfileSerializer(serializers.ModelSerializer):
    """
    serializer for customer profile
    """
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'phone', 'gender', 'profile_img']

class SellerProfileSerializer(serializers.ModelSerializer):
    """
    serializer for seller profile
    """
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'phone', 'gender', 'profile_img']

class SellerChangePasswordSerializer(serializers.Serializer):
    """
    serializer for seller change password
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs


