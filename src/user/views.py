import datetime

from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .serializers import (
    CreateUserSerializer, LoginSerializer, UpdatePasswordSerializer, CustomUserSerializer,
    UserActivitySerializer)
from .models import UserActivity, CustomUser
from inventory.custom_methods import IsAuthenticatedCustom
from inventory.utils import get_access_token


def add_user_activities(user, activity):
    qs = UserActivity.objects.create(
        user_id=user.id,
        username=user.username,
        # fullname = user.fullname,
        action=activity
    )


class CreateUserView(ModelViewSet):
    http_method_names = ['post']
    queryset = CustomUser.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = IsAuthenticatedCustom,

    def create(self, request, **kwargs):
        valid_request = self.serializer_class(data=request.data)
        valid_request.is_valid(raise_exception=True)

        CustomUser.objects.create(**valid_request.validated_data)
        add_user_activities(request.user, activity='added new user')
        return Response(
            {'success': 'User created Successfully.'},
            status=status.HTTP_201_CREATED
        )


class LoginView(ModelViewSet):
    http_method_names = ['post']
    queryset = CustomUser.objects.all()
    serializer_class = LoginSerializer

    def create(self, request, **kwargs):
        valid_request = self.serializer_class(data=request.data)
        valid_request.is_valid(raise_exception=True)

        new_user = valid_request.validated_data["is_new_user"]
        if new_user:
            user = CustomUser.objects.filter(
                username=valid_request.validated_data['username']
            )
            if user:
                user = user[0]
                if not user.password:
                    return Response({'user_id': user.id})
                else:
                    raise Exception("User has password already.")
            else:
                raise Exception("User with username not found.")
        user = authenticate(
            username=valid_request.validated_data['username'],
            password=valid_request.validated_data.get('password', None)
        )
        if not user:
            return Response(
                {'error': 'Invalid username or password.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        access = get_access_token({"user_id": user.id}, 1)
        user.last_login = datetime.datetime.now()
        user.save()
        add_user_activities(request.user, activity='logged in')

        return Response({"access": access})


class UpdatePasswordView(ModelViewSet):
    serializer_class = UpdatePasswordSerializer
    queryset = CustomUser.objects.all()
    http_method_names = ['post']

    def create(self, request, **kwargs):
        valid_request = self.serializer_class(data=request.data)
        valid_request.is_valid(raise_exception=True)

        user = CustomUser.objects.filter(id=valid_request.validated_data['user_id'])

        if not user:
            raise Exception("User with id not found")
        user = user[0]
        user.set_password(valid_request.validated_data['password'])
        add_user_activities(user, activity='updated the password')

        user.save()


class MeView(ModelViewSet):
    serializer_class = CustomUserSerializer
    http_method_names = ['get']
    permission_classes = IsAuthenticatedCustom,

    def list(self, request, **kwargs):
        data = self.serializer_class(request.user).data
        return Response(data)


class UserActivityView(ModelViewSet):
    serializer_class = UserActivitySerializer
    http_method_names = ['get']
    queryset = UserActivity.objects.all()
    permission_classes = IsAuthenticatedCustom,


class UserView(ModelViewSet):
    serializer_class = CustomUserSerializer
    http_method_names = ['get']
    queryset = CustomUser.objects.prefetch_related("user_activities")
    permission_classes = IsAuthenticatedCustom,

    def list(self, request, **kwargs):
        users = self.queryset().filter(is_superuser=False)
        data = self.serializer_class(users, many=True).data
        return Response(data)
