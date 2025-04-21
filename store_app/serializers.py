from rest_framework import serializers
from store_app.models import Store,StoreEmployee
from users_app.models import CustomUser
from django.contrib.auth.models import Group,Permission

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'name', 'address','city']
        read_only_fields = ['id']

class StoreEmployeeCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True, required=True)
    firstname = serializers.CharField(write_only=True, required=True)
    lastname = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(write_only=True, required=True)
    phone = serializers.CharField(write_only=True, required=True)
    gender = serializers.BooleanField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    store_id = serializers.PrimaryKeyRelatedField(queryset=Store.objects.all(), required=True)

    class Meta:
        model = StoreEmployee
        fields = [
            'id', 'user_id', 'store_id', 'is_manager', 'is_operator', 'created_at',
            'username', 'firstname', 'lastname', 'email', 'phone', 'gender', 'password'
        ]
        read_only_fields = ['id', 'created_at', 'user_id']

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
        if validated_data.get('is_manager'):
            group, _ = Group.objects.get_or_create(name='SellerManagers')
            user.groups.add(group)
        if validated_data.get('is_operator'):
            group, _ = Group.objects.get_or_create(name='SellerOperators')
            user.groups.add(group)

        # Create StoreEmployee
        emp = StoreEmployee.objects.create(
            user_id=user,
            store_id=store,
            **validated_data
        )
        return emp
