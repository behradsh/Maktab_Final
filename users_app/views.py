from django.shortcuts import render
from rest_framework import (generics,status,views,permissions)
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from rest_framework.views import APIView
from .serializers import (UserRegisterSerializer,
                          SellerRegisterSerializer,
                          LoginSerializer,
                          LogOutSerializer,
                          UserDetailSerializer,
                          ChangePasswordSerializer)
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
# Create your views here.
class CustomerRegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.filter(is_customer=True)
    permission_classes = (AllowAny,)
    serializer_class = UserRegisterSerializer

class SellerRegisterView(generics.CreateAPIView):
    serializer_class = SellerRegisterSerializer
    queryset = CustomUser.objects.filter(is_customer=False)
    permission_classes = (AllowAny,)


class UserDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = (IsAuthenticated,)
    def get_object(self):
        return self.request.user

class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticated,)
    def get_object(self):
        return self.request.user
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            #check old password
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({"old password":["Wrong password"]},
                                status=status.HTTP_400_BAD_REQUEST)
            #Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message":["Your password has been Changed"]},)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    def post(self,request):
        print(f"Received {request.method} request to {request.path}")
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
        # serializer.is_valid(raise_exception=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogOutAPIView(APIView):
    serializer_class = LogOutSerializer
    permission_classes = [IsAuthenticated]
    def post(self,request):
        serializer = self.serializer_class(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # serializer.save()
        logout(request)
        return Response("Successfully LoggedOut",status=status.HTTP_204_NO_CONTENT)

@login_required(login_url="/login/")
def customer_dashboard(request):
    return HttpResponse(_("Customer Dashboard"))

@login_required(login_url="/login/")
def seller_dashboard(request):
    return HttpResponse(_("Seller Dashboard"))