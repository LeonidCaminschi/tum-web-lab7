from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from .models import Movie
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.core.paginator import Paginator

class RegisterView(APIView):

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        role = request.data.get('role')
        permissions = request.data.get('permissions', [])

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password)

        # Create a group for the role if it doesn't exist
        group, created = Group.objects.get_or_create(name=role)
        user.groups.add(group)

        # Add permissions to the user
        for permission in permissions:
            perm = Permission.objects.get(codename=permission)
            user.user_permissions.add(perm)

        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        refresh['role'] = list(user.groups.values_list('name', flat=True))
        refresh['permissions'] = list(user.user_permissions.values_list('codename', flat=True))

        return Response({
            'message': 'User registered successfully!',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=201)
    
class LoginView(APIView):

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is None:
            return Response({'error': 'Invalid credentials'}, status='400')
        refresh = RefreshToken.for_user(user)
        refresh['role'] = list(user.groups.values_list('name', flat=True))
        refresh['permissions'] = list(user.user_permissions.values_list('codename', flat=True))
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
