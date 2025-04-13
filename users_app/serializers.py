from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.models import Group
from django.contrib.auth import login,logout,authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import (RefreshToken, AccessToken,TokenError)

class CustomerRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'phone_number', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            phone_number=validated_data.get('phone_number'),
            password=validated_data['password'],
            is_customer=True
        )
        customer_group = Group.objects.get(name='Customers')
        user.groups.add(customer_group)
        return user

class SellerRegistrationSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(max_length=255, required=False)
    store_address = serializers.CharField(max_length=500, required=False)
    seller_type = serializers.ChoiceField(choices=['Owner', 'Manager', 'Operator'], default='Owner')

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'phone_number', 'password', 'store_name', 'store_address', 'seller_type']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        store_name = validated_data.pop('store_name', None)
        store_address = validated_data.pop('store_address', None)
        seller_type = validated_data.pop('seller_type', 'Owner')

        user = CustomUser.objects.create_user(
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            phone_number=validated_data.get('phone_number'),
            password=validated_data['password'],
            is_customer=False
        )

        # Assign group based on seller_type
        group_name = f'Seller {seller_type}s'
        seller_group = Group.objects.get(name=group_name)
        user.groups.add(seller_group)

        # If Seller Owner, create a Store
        if seller_type == 'Owner' and store_name and store_address:
            from src.config.store_app.models import Store  # Import here to avoid circular imports
            Store.objects.create(
                owner=user,
                name=store_name,
                address=store_address
            )
        # Managers/Operators will be linked to stores later via StoreEmployee

        return user

class LoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True, )
    username = serializers.CharField(max_length=25, min_length=6)
    token = serializers.SerializerMethodField()
    def get_token(self,obj):
        user = CustomUser.objects.get(username=obj['username'])
        return {
            'refresh':user.tokens()['refresh'],
            'access':user.tokens()['access'],
        }
    class Meta:
        model = CustomUser
        fields = ('username','password','token')
    def validate(self, attrs):
        username = attrs.get('username', '')
        password = attrs.get('password', '')
        user = authenticate(username=username, password=password)
        if not user:
            raise AuthenticationFailed('Invalid Credentials,Try Again')
        if not user.is_active:
            raise AuthenticationFailed('Your account is inactive,Contact Admin')
        return {
            'email': user.email,
            'username': user.username,
            'tokens': user.tokens
        }

class LogOutSerializer(serializers.ModelSerializer):
    refresh = serializers.CharField()
    class Meta:
        model = CustomUser
        fields = "__all__"
    def validate(self,attrs):
        self.token = attrs['refresh']
        return attrs
    def save(self,**kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')