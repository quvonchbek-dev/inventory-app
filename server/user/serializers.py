from rest_framework import serializers
from .models import CustomUser, UserActivity


class CreateUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    role = serializers.ChoiceField(CustomUser.Role.choices)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=100)
    is_new_user = serializers.BooleanField(default=False, required=False)


class UpdatePasswordSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    password = serializers.CharField()


class CustomUserSerializer(serializers.Serializer):
    class Meta:
        model = CustomUser
        exclude = 'password',


class UserActivitySerializer(serializers.Serializer):
    class Meta:
        model = UserActivity
        fields = '__all__'
