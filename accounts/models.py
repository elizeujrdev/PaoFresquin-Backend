from django.contrib.auth.models import AbstractUser
from django.db import models


class Perfil(models.TextChoices):
    ADMIN = "ADMIN", "Administrador"
    GERENTE = "GERENTE", "Gerente"
    ATENDENTE = "ATENDENTE", "Atendente"
    PADEIRO = "PADEIRO", "Padeiro"


class User(AbstractUser):
    email = models.EmailField("e-mail", unique=True)
    perfil = models.CharField(max_length=20, choices=Perfil.choices, default=Perfil.ATENDENTE)
    loja = models.CharField(max_length=100, default="Loja Centro")
    ativo = models.BooleanField(default=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "first_name"]

    class Meta:
        verbose_name = "usuário"
        verbose_name_plural = "usuários"

    @property
    def nome_exibicao(self):
        return self.get_full_name() or self.username

    def pode_cancelar_venda(self):
        return self.perfil in (Perfil.ADMIN, Perfil.GERENTE)

    def pode_gerenciar_funcionarios(self):
        return self.perfil in (Perfil.ADMIN, Perfil.GERENTE)

    def pode_relatorios(self):
        return self.perfil != Perfil.PADEIRO

    def pode_vendas(self):
        return self.perfil in (Perfil.ADMIN, Perfil.GERENTE, Perfil.ATENDENTE)
