
# Create your views here.
from django.shortcuts import render
# Create your views here.
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterUserSerializer
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['user_name'] = user.user_name
        token['email']=user.email 
        token['phone_number']=user.phone_number
        token['location']=user.location
        # ...
        return token
    
class MyTokenObtainPairView(TokenObtainPairView): 
    serializer_class=MyTokenObtainPairSerializer

class CustomUserCreate(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        reg_serializer = RegisterUserSerializer(data=request.data)
        if reg_serializer.is_valid():
            user = reg_serializer.save()
            if user:
                json = reg_serializer.data
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(reg_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
def getRoutes(request):
    routes=[
        
        '/api/token',
        '/api/token/refresh',
    ]
    return Response(routes)

class BlacklistTokenView(APIView):
    permission_classes = [AllowAny]
    authentication_classes=()
    def post(self,request):
        try:
            refresh_token =request.data["refresh_token"]
            token=RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
