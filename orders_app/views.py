from django.shortcuts import render
from rest_framework import viewsets, permissions,generics,views
from .models import Orders,OrderItems,CartItem,Cart
from .serializers import OrderSerializer,OrderItemSerializer,CartSerializer,CartItemSerializer
from rest_framework.response import Response
from rest_framework.status import HTTP_406_NOT_ACCEPTABLE, HTTP_200_OK, HTTP_400_BAD_REQUEST
from products_app.models import Product
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

def get_cart(request):
    cart = request.COOKIES.get('cart', None)
    if cart:
        cart = cart.replace('\'', '"')
        cart = json.loads(cart)
        return cart
    return None


class AddToCartAPIView(views.APIView):
    permission_classes = [AllowAny]
    serializer_class = ProductSerializer
    model = Product

    def post(self, request):
        pk = request.POST.get('pk')
        count = int(request.POST.get('count'))
        product = self.model.objects.get(id=pk)
        if count < product.quantity:
            cart = get_cart(request)
            pk = pk
            product_name = product.name
            price = product.price
            discount = "0"
            image = product.image
            if not cart:
                temp_cart = {pk: {"product_name": product_name, "price": price, "count": count,
                                  "image": image}}
                cart = f'{temp_cart}'
            else:
                if pk in cart:
                    cart[pk]["count"] += count
                else:
                    cart.update({pk: {"product_name": product_name, "price": price, "count": count,
                                      "image": image}})
            response = Response({'cart': 'ok'})
            expire = datetime.datetime.now() + datetime.timedelta(weeks=1)
            expire_string = expire.strftime("%a, %d-%b-%Y %H:%M:%S")
            response.set_cookie("cart", cart, expires=expire_string)
            response.data = {'cart_count': len(cart)}
            return response
        else:
            return Response({'product': 'not enough'}, status=HTTP_406_NOT_ACCEPTABLE)


class UpdateCartAPIView(views.APIView):
    permission_classes = [AllowAny]
    serializer_class = ProductSerializer
    model = Product

    def get(self, request):
        cart = get_cart(request)
        if cart:
            return Response(cart)
        else:
            return Response({'cart': 'empty'})

class RemoveFromCartAPIView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        pk = request.GET.get('pk')
        cart = get_cart(request)
        cart.pop(pk)
        response = Response({'cart':'ok'})
        expire = datetime.datetime.now() + datetime.timedelta(weeks = 1)
        expire_string = expire.strftime("%a, %d-%b-%Y %H:%M:%S")
        response.set_cookie("cart", cart, expires=expire_string)
        response.data = {'cart_count': len(cart)}
        return response


class CartCountAPIView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        cart = get_cart(request)
        if cart:
            return Response({'cart_count': len(cart)}, status=HTTP_200_OK)
        else:
            return Response({'cart_count': 0}, status=HTTP_200_OK)

class TotalPriceAPIView(views.APIView):
    permission_classes = [IsAuthenticated]


class SubmitOrderAPIView(views.APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    model = Orders
    detail_model = OrderItems
    request = None

    def clear_cookie(self, response):
        response.delete_cookie('cart')

    def get_address(self):
        address_id = self.request.data['address_id']
        return Address.objects.get(id=address_id)

    def get_user(self):
        return CustomUser.objects.get(id=self.request.user.id)

    def post(self, request):
        request = request
        address = self.get_address()
        user = self.get_user()
        cart = get_cart(request)
        total_discount = 0
        details = []
        total_price = 0

        for key, val in cart.items():
            temp = {}
            product = Product.objects.get(id=key)
            temp['product'] = product
            temp['quantity'] = val['count']
            temp['price'] = val['price']
            temp['discount'] = val['discount'] * val['count']
            total_price += (val['price'] * val['count'])
            total_discount += (val['discount'] * val['count'])
            details.append(temp)
            product.quantity -= val['count']
            product.save()

        order = {'total_paid': total_price, 'total_discount': total_discount,
                  'customer': user, 'address': address}

        order = self.model.objects.create(**order)

        for detail in details:
            self.detail_model.objects.create(order=order, **detail)

        response = Response(status=HTTP_200_OK)
        self.clear_cookie(response)
        return response


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
