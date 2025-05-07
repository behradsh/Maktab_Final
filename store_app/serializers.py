from rest_framework import serializers
from store_app.models import Store,StoreEmployee
from users_app.models import CustomUser
from django.contrib.auth.models import Group,Permission
from django.utils.translation import gettext_lazy as _

class StoreSerializer(serializers.ModelSerializer):
    """
    serializer for store model
    """
    created_at_shamsi = serializers.SerializerMethodField()
    updated_at_shamsi = serializers.SerializerMethodField()
    class Meta:
        model = Store
        fields = ['id', 'name', 'address','city','created_at_shamsi','updated_at_shamsi']
        read_only_fields = ['id']

    def get_created_at_shamsi(self,obj):
        return obj.created_at_shamsi

    def get_updated_at_shamsi(self,obj):
        return obj.updated_at_shamsi

class StoreEmployeeCreateSerializer(serializers.ModelSerializer):
    """
    serializer for creating store employee model
    """
    created_at_shamsi = serializers.SerializerMethodField()
    username = serializers.CharField(write_only=True, required=True,)  # Include username from CustomUser
    firstname = serializers.CharField(write_only=True, required=True,)
    lastname = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(write_only=True, required=True)
    phone = serializers.CharField(write_only=True, required=True)
    gender = serializers.BooleanField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    is_manager = serializers.BooleanField(write_only=True,required=False)
    is_operator = serializers.BooleanField(write_only=True,required=False)

    class Meta:
        model = StoreEmployee
        fields = [
            'id', 'user_id', 'store_id', 'is_manager', 'is_operator', 'created_at',
            'username', 'firstname', 'lastname', 'email', 'phone', 'gender', 'password','created_at_shamsi',
        ]
        read_only_fields = ['id', 'created_at', 'user_id',]

    def get_created_at_shamsi(self,obj):
        return obj.created_at_shamsi

    def validate(self, attrs):
        if not attrs.get('is_manager') and not attrs.get('is_operator'):
            raise serializers.ValidationError("Employee must be at least a manager or an operator.")
        return attrs

    def create(self, validated_data):
        # Pop user-related fields
        username = validated_data.pop('username')
        firstname = validated_data.pop('firstname')
        lastname = validated_data.pop('lastname')
        email = validated_data.pop('email')
        phone = validated_data.pop('phone')
        gender = validated_data.pop('gender')
        password = validated_data.pop('password')
        store = validated_data.pop('store_id')
        is_manager = validated_data.pop('is_manager', False)
        is_operator = validated_data.pop('is_operator', False)

        # Create CustomUser
        user = CustomUser.objects.create(
            username=username,
            email=email,
            phone=phone,
            first_name=firstname,
            last_name=lastname,
            gender=gender,
            is_customer=False,
            is_staff=False
        )
        user.set_password(password)
        user.save()

        # Assign groups
        if is_manager:
            try:
                group = Group.objects.get(name='SellerManagers')
                user.groups.add(group)
                user.save()
            except Exception as e:
                group = None
        if is_operator:
            try:
                group = Group.objects.get(name='SellerOperators')
                user.groups.add(group)
                user.save()
            except Exception as e:
                group = None

        # Create StoreEmployee
        emp = StoreEmployee.objects.create(
            user_id=user,
            store_id=store,
            is_manager=is_manager,
            is_operator=is_operator,
            **validated_data
        )
        emp.save()
        return emp


class StoreEmployeeSerializer(serializers.ModelSerializer):
    """
        serializer for store employee model
    """
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        required=True,
        error_messages={
            'does_not_exist': _('User does not exist.'),
            'required': _('User ID is required.')
        }
    )
    store_id = serializers.PrimaryKeyRelatedField(
        queryset=Store.objects.all(),
        required=False  # Will set in the view
    )
    username = serializers.CharField(source='user_id.username', read_only=True)
    email = serializers.EmailField(source='user_id.email', read_only=True)
    phone = serializers.CharField(source='user_id.phone', read_only=True)
    store_name = serializers.CharField(source='store_id.name', read_only=True)
    created_at_shamsi = serializers.SerializerMethodField()

    class Meta:
        model = StoreEmployee
        fields = [
            'id',
            'user_id',
            'username',
            'email',
            'phone',
            'store_id',
            'store_name',
            'is_manager',
            'is_operator',
            'created_at',
            'created_at_shamsi'
        ]
        read_only_fields = ['created_at', 'username', 'email', 'phone', 'store_name']

    def get_created_at_shamsi(self, obj):
        return obj.created_at_shamsi

    def validate(self, data):
        # Ensure at least one role is selected
        if not data.get('is_manager') and not data.get('is_operator'):
            raise serializers.ValidationError(_("Employee must have at least one role (manager or operator)."))

        # Prevent both roles being True if that's not allowed in your business logic
        if data.get('is_manager') and data.get('is_operator'):
            raise serializers.ValidationError(_("User cannot be both manager and operator."))

        return data

