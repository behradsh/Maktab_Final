from django.shortcuts import render
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
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
from .service import Cart,CART_SESSION_ID
import json
# Create your views here.

class CustomerOrderHistoryView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Orders.objects.filter(customer=self.request.user)

#get or create session cart
def get_session_cart(request):
    if 'cart' not in request.session:
        request.session['cart'] = {}  # {product_id: quantity}
    return request.session['cart']

#get user cart
def get_user_cart(user):
    cart, created = Cart.objects.get_or_create(user=user)
    return cart

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


class CustomerAddressesAPIView(views.APIView):
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


class AddAddressAPIView(views.APIView):
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
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    queryset = Orders.objects.all()





# Cart and Checkout Views
class CartView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated,IsCustomer]
    serializer_class = CartSerializer

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_customer:
            cart = get_user_cart(request.user)
            serializer = self.get_serializer(cart)
            return Response(serializer.data)
        else:
            session_cart = request.session.get('cart', {})
            cart_data = []
            total = 0
            for product_id, quantity in session_cart.items():
                try:
                    product = Product.objects.get(id=product_id)
                    if quantity <= product.quantity:
                        subtotal = product.price * quantity
                        cart_data.append({
                            'product': ProductSerializer(product).data,
                            'quantity': quantity,
                            'subtotal': subtotal
                        })
                        total += subtotal
                except Product.DoesNotExist:
                    continue
            return Response({
                'items': cart_data,
                'total': total
            })

    def post(self, request, *args, **kwargs):
        serializer = CartItemSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            product = serializer.validated_data['product']
            quantity = serializer.validated_data['quantity']
            if request.user.is_authenticated and request.user.is_customer:
                cart = get_user_cart(request.user)
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    defaults={'quantity': quantity}
                )
                if not created:
                    cart_item.quantity += quantity
                    cart_item.save()
                return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)
            else:
                session_cart = request.session.get('cart', {})
                product_id_str = str(product.id)
                session_cart[product_id_str] = session_cart.get(product_id_str, 0) + quantity
                request.session['cart'] = session_cart
                request.session.modified = True
                return Response({
                    'detail': 'Product added to cart',
                    'product_id': product.id,
                    'quantity': quantity
                }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CartItemUpdateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated,IsCustomer,]
    serializer_class = CartItemSerializer

    def patch(self, request, pk, *args, **kwargs):
        try:
            product = Product.objects.get(id=pk)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            quantity = serializer.validated_data['quantity']
            if request.user.is_authenticated and request.user.is_customer:
                cart = get_user_cart(request.user)
                try:
                    cart_item = cart.items.get(product=product)
                    cart_item.quantity = quantity
                    cart_item.save()
                    return Response(CartSerializer(cart).data)
                except CartItem.DoesNotExist:
                    return Response({'detail': 'Product not in cart'}, status=status.HTTP_404_NOT_FOUND)
            else:
                session_cart = request.session.get('cart', {})
                product_id_str = str(pk)
                if product_id_str not in session_cart:
                    return Response({'detail': 'Product not in cart'}, status=status.HTTP_404_NOT_FOUND)
                session_cart[product_id_str] = quantity
                request.session['cart'] = session_cart
                request.session.modified = True
                return Response({
                    'detail': 'Cart updated',
                    'product_id': pk,
                    'quantity': quantity
                })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CartItemDeleteView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated,IsCustomer]

    def delete(self, request, pk, *args, **kwargs):
        try:
            product = Product.objects.get(id=pk)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        if request.user.is_authenticated and request.user.is_customer:
            cart = get_user_cart(request.user)
            try:
                cart_item = cart.items.get(product=product)
                cart_item.delete()
                return Response(CartSerializer(cart).data)
            except CartItem.DoesNotExist:
                return Response({'detail': 'Product not in cart'}, status=status.HTTP_404_NOT_FOUND)
        else:
            session_cart = request.session.get('cart', {})
            product_id_str = str(pk)
            if product_id_str not in session_cart:
                return Response({'detail': 'Product not in cart'}, status=status.HTTP_404_NOT_FOUND)
            del session_cart[product_id_str]
            request.session['cart'] = session_cart
            request.session.modified = True
            return Response({'detail': 'Product removed from cart'}, status=status.HTTP_204_NO_CONTENT)

class CheckoutView2(generics.GenericAPIView):
    permission_classes = [IsAuthenticated,IsCustomer]
    serializer_class = OrderSerializer

    def post(self, request, *args, **kwargs):
        cart = get_user_cart(request.user)
        items = cart.items.all()
        if not items:
            return Response({'detail': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        address_id = request.data.get('shipping_address_id')
        try:
            address = request.user.addresses.get(id=address_id)
        except address.DoesNotExist:
            return Response({'detail': 'Address not found'}, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            store_items = {}
            for item in items:
                store_id = item.product.store.id
                if store_id not in store_items:
                    store_items[store_id] = []
                store_items[store_id].append(item)

            orders = []
            for store_id, cart_items in store_items.items():
                store = Store.objects.get(id=store_id)
                total_amount = 0
                order = Orders.objects.create(
                    user=request.user,
                    store=store,
                    total_amount=0,
                    shipping_address=address
                )
                for item in cart_items:
                    if item.quantity > item.product.stock:
                        return Response({
                            'detail': f'Insufficient stock for {item.product.name}'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    price = item.product.price
                    discounts = item.product.store.discounts.filter(
                        start_date__lte=timezone.now(),
                        end_date__gte=timezone.now()
                    )
                    if discounts.exists():
                        discount = discounts.first()
                        price = price * (1 - discount.percentage / 100)
                    OrderItems.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=price
                    )
                    total_amount += price * item.quantity
                    item.product.stock -= item.quantity
                    item.product.save()
                order.total_amount = total_amount
                order.save()
                orders.append(OrderSerializer(order).data)
                cart.items.filter(product__store=store).delete()

        return Response({
            'detail': 'Order placed successfully',
            'orders': orders
        }, status=status.HTTP_201_CREATED)


class SellerOrderListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated,IsStoreOwnerOrManager]
    serializer_class = OrderSerializer

    def get_queryset(self):
        store = get_user_store(self.request.user)
        return store.orders.all()

class SellerOrderUpdateView(generics.UpdateAPIView):
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
    permission_classes = [IsAuthenticated, IsCustomer]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # Debug: log raw request data and session
        print("[DEBUG] request.data:", request.data)
        print("[DEBUG] request.session keys:", list(request.session.keys()))
        for item in list(request.session.keys()):
            cd = request.data.get(item)
            print("[DEBUG] cart_data:", cd)

        # 1. Extract cart from POST payload
        cart_data = request.data.get('cart')
        print("[DEBUG] cart_data:", cart_data)
        if not isinstance(cart_data, dict) or not cart_data:
            print("[DEBUG] Empty or invalid cart_data")
            return Response({"error": "Cart is empty or invalid"}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Create Order
        user = request.user
        try:
            address = Address.objects.get(customer=user)
        except Address.DoesNotExist:
            return Response({"error": "Shipping address not found"}, status=status.HTTP_400_BAD_REQUEST)
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

        # 3. Process each cart item
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

            # Create OrderItem; manager sets price if not provided
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

        # 4. Finalize order total
        order.total_amount = total_amount
        order.save()
        print(f"[DEBUG] Order {order.id} saved with total_amount {order.total_amount}")

        # 5. Respond
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
