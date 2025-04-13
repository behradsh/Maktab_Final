from django.shortcuts import render
from rest_framework import (generics,status,views)
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser
from .serializers import (CustomerRegistrationSerializer,SellerRegistrationSerializer,LoginSerializer,LogOutSerializer)
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
# Create your views here.
class CustomerRegistrationView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomerRegistrationSerializer
    permission_classes = [AllowAny]

class SellerRegistrationView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = SellerRegistrationSerializer
    permission_classes = [AllowAny]

# class CustomerRegisterView(generics.CreateAPIView):
#     permission_classes = [AllowAny]
#     serializer_class = CustomerRegistrationSerializer
#     def post(self,request):
#         serializer = self.serializer_class(data=request.data)
#         if serializer.is_valid():
#             # serializer.is_valid(raise_exception=True)
#             serializer.save()
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         user_data = serializer.data
#         return Response(user_data,status=status.HTTP_201_CREATED)
#
# class SellerRegisterView(generics.CreateAPIView):
#     permission_classes = [AllowAny]
#     serializer_class = SellerRegistrationSerializer
#     def post(self,request):
#         serializer = self.serializer_class(data=request.data)
#         if serializer.is_valid():
#             # serializer.is_valid(raise_exception=True)
#             serializer.save()
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         user_data = serializer.data
#         return Response(user_data,status=status.HTTP_201_CREATED)

class LoginAPIView(generics.GenericAPIView):
    permission_classes = []
    serializer_class = LoginSerializer
    def post(self,request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
        # serializer.is_valid(raise_exception=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogOutAPIView(generics.GenericAPIView):
    serializer_class = LogOutSerializer
    permission_classes = []
    def post(self,request):
        # serializer = self.serializer_class(data=request.data)
        logout(request)
        return Response("Successfully LoggedOut",status=status.HTTP_204_NO_CONTENT)