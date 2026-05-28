from decimal import Decimal

from django.db import models


class Cliente(models.Model):
    nome = models.CharField(max_length=200)
    cpf = models.CharField(max_length=14, unique=True)
    telefone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    endereco = models.CharField(max_length=300, blank=True)
    negativado = models.BooleanField(default=False)
    score_serasa = models.PositiveIntegerField(null=True, blank=True)
    restricoes_serasa = models.PositiveSmallIntegerField(default=0)
    ultima_consulta_serasa = models.DateTimeField(null=True, blank=True)
    saldo_devedor = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    ativo = models.BooleanField(default=True)
    cliente_desde = models.DateField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome

    def pode_fiado(self):
        return not self.negativado and self.ativo
