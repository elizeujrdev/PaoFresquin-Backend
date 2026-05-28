from django.contrib.auth import authenticate
from rest_framework import serializers

from accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source="nome_exibicao", read_only=True)
    iniciais = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "perfil",
            "loja",
            "nome",
            "iniciais",
        ]

    def get_iniciais(self, obj):
        parts = obj.nome_exibicao.split()
        return "".join(p[0].upper() for p in parts[:2]) or obj.username[:2].upper()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            username=attrs["username"],
            password=attrs["password"],
        )
        if not user or not user.is_active or not user.ativo:
            raise serializers.ValidationError(
                "Credenciais inválidas. Verifique usuário e senha ou contate o administrador."
            )
        attrs["user"] = user
        return attrs
