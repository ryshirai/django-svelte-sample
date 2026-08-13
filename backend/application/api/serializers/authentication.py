from typing import Any

from rest_framework import serializers


class CreateRegistrationInputSerializer(serializers.Serializer[Any]):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)


class CreateSessionInputSerializer(serializers.Serializer[Any]):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)


class CurrentUserOutputSerializer(serializers.Serializer[Any]):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    is_staff = serializers.BooleanField()
