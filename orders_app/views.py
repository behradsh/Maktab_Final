from rest_framework import viewsets, permissions,generics,views
from .models import Orders,OrderItems,CartItem,Cart
from .serializers import OrderSerializer,OrderItemSerializer,CartSerializer,CartItemSerializer
from rest_framework.response import Response
from rest_framework.status import HTTP_406_NOT_ACCEPTABLE, HTTP_200_OK, HTTP_400_BAD_REQUEST
from products_app.models import Product
from decimal import Decimal
from products_app.serializers import ProductSerializer
from rest_framework.permissions import AllowAny,IsAuthenticated
from users_app.models import Address,CustomUser
from users_app.serializers import AddressSerializer
from store_app.models import Store
from core_app.custom_permissions import *
from rest_framework import permissions,status
import datetime
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
import json
# Create your views here.

class CustomerOrderHistoryView(generics.ListAPIView):
    """
    view for listing customer order's history
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Orders.objects.filter(customer=self.request.user)

class CustomerOrderDetailsView(generics.ListAPIView):
    """
    view for listing customer order's details includes orderitems
    """
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get the order ID from the URL
        order_id = self.kwargs.get('pk')  # Use 'pk' to match the URL parameter
        return OrderItems.objects.filter(order_id=order_id)


#TODO - refactor this part
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
    except Exception:
        raise Exception('Not assigned to a store')

#TODO implementing Front pages
class CustomerAddressesAPIView(views.APIView):
    """
    view for retrieving customer address for buy products
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer
    model = Address

    def get(self, request):
        pk = request.user.id
        address = self.model.objects.filter(customer=pk)
        if address:
            serializer = self.serializer_class(address, many=True)
            return Response(serializer.data)
        return Response({'cart': "empty"})

#TODO implementing Front pages
class AddAddressAPIView(views.APIView):
    """
        view for retrieve and select customer address for buy products
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer
    model = Address
    customer_model = CustomUser

    def get(self, request):
        addresses = self.model.objects.filter(customer=request.user.id)
        if len(addresses) >= 3:
            messages.warning(request, "you have reached 3 address limit from your panel edit or delete one.")
        return Response({'address_count': len(addresses)})

    def post(self, request):
        customer = self.customer_model.objects.get(id=request.user.id)
        data = json.loads(request.data['address'])
        print(data)
        serializer = self.serializer_class(data=data)
        serializer.is_valid()
        serializer.save(customer=customer)
        return Response(serializer.data, status=HTTP_200_OK)

class OrdersListAPIView(generics.ListAPIView):
    """
    view for listing orders for a specific store seller
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    queryset = Orders.objects.all()



class SellerOrderListView(generics.ListCreateAPIView):
    """
        view for listing orders for a specific store seller
    """
    permission_classes = [permissions.IsAuthenticated,IsStoreOwnerOrManager]
    serializer_class = OrderSerializer

    def get_queryset(self):
        store = get_user_store(self.request.user)
        return store.orders.all()

class SellerOrderUpdateView(generics.UpdateAPIView):
    """
    view for update orders for a specific store
    """
    permission_classes = [permissions.IsAuthenticated,IsStoreOwnerOrManager]
    serializer_class = OrderSerializer

    def get_queryset(self):
        store = get_user_store(self.request.user)
        return store.orders.all()

    def perform_update(self, serializer):
        if self.request.user.groups.filter(name='SellerOperators').exists():
            raise Exception('Operators cannot update orders')
        serializer.save()



class CheckoutView(generics.CreateAPIView):
    """
    not a real checkout view,this view just take data of shopping cart from front-end and
    create order,orderitems
    """
    permission_classes = [IsAuthenticated, IsCustomer]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # Debug: log raw request data and session
        print("[DEBUG] request.data:", request.data)
        print("[DEBUG] request.session keys:", list(request.session.keys()))
        for item in list(request.session.keys()):
            cd = request.data.get(item)
            print("[DEBUG] cart_data:", cd)

        # get cart from POST request
        cart_data = request.data.get('cart')
        print("[DEBUG] cart_data:", cart_data)
        if not isinstance(cart_data, dict) or not cart_data:
            print("[DEBUG] Empty or invalid cart_data")
            return Response({"error": "Cart is empty or invalid"}, status=status.HTTP_400_BAD_REQUEST)

        # Create Order
        user = request.user
        try:
            address = Address.objects.get(customer=user)
        except Address.DoesNotExist:
            return Response({"error": "Shipping address not found"}, status=status.HTTP_400_BAD_REQUEST)
        #TODO - refactor code for select store automatically
        store = Store.objects.get(id=3)  # adjust as needed

        order = Orders.objects.create(
            customer=user,
            address=address,
            status='pending',
            total_amount=Decimal('0.00'),
            store=store,
            discount=0
        )
        print("[DEBUG] Created order id:", order.id)

        # looping through each cart item
        total_amount = Decimal('0.00')
        for prod_id_str, item in cart_data.items():
            print(f"[DEBUG] Processing cart item: {prod_id_str} -> {item}")
            try:
                prod_id = int(prod_id_str)
                quantity = int(item.get('quantity', 0))
                price = Decimal(item.get('price', '0'))
            except (ValueError, TypeError) as e:
                print(f"[DEBUG] Invalid item data for product {prod_id_str}:", e)
                return Response({"error": "Invalid item format"}, status=status.HTTP_400_BAD_REQUEST)

            if quantity <= 0:
                print(f"[DEBUG] Skipping product {prod_id}: non-positive quantity {quantity}")
                continue

            # Fetch product
            try:
                product = Product.objects.get(id=prod_id)
                print(f"[DEBUG] Fetched product {product.name}")
            except Product.DoesNotExist:
                print(f"[DEBUG] Product {prod_id} does not exist")
                return Response({"error": f"Product {prod_id} does not exist"}, status=status.HTTP_400_BAD_REQUEST)

            # Create OrderItem
            order_item = OrderItems.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=price,
                discount=item.get('discount', 0)
            )
            print(f"[DEBUG] Created order item id {order_item.id} price {order_item.price}")
            total_amount += order_item.price
            print(f"[DEBUG] Processing product {prod_id} and change its quantity")
            print(f"before change-->{product.quantity}")
            product.quantity -= quantity
            product.save()
            print(f"after change-->{product.quantity}")

        # set order total amount
        order.total_amount = total_amount
        order.save()
        print(f"[DEBUG] Order {order.id} saved with total_amount {order.total_amount}")


        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
