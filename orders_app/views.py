from django.shortcuts import render
from rest_framework import viewsets, permissions,generics
from .models import Orders,OrderItems,CartItem,Cart
from .serializers import OrderSerializer,OrderItemSerializer,CartSerializer,CartItemSerializer
from rest_framework.response import Response
from products_app.models import Product
from products_app.serializers import ProductSerializer
from rest_framework.permissions import AllowAny,IsAuthenticated
from store_app.models import Store
from core_app.custom_permissions import *
from rest_framework import permissions,status
from django.db import transaction
from django.utils import timezone
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

class CheckoutView(generics.GenericAPIView):
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