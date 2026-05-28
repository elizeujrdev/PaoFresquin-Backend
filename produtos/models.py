from decimal import Decimal

from django.db import models


class UnidadeMedida(models.TextChoices):
    PESO = "PESO", "Peso (kg)"
    UNIDADE = "UNIDADE", "Unidade"


class Categoria(models.Model):
    nome = models.CharField(max_length=80, unique=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "categorias"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Produto(models.Model):
    nome = models.CharField(max_length=120)
    codigo_barras = models.CharField(max_length=32, unique=True, blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="produtos")
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2)
    preco_custo = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    unidade = models.CharField(max_length=10, choices=UnidadeMedida.choices, default=UnidadeMedida.UNIDADE)
    descricao = models.TextField(blank=True)
    estoque_atual = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal("0"))
    estoque_minimo = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal("0"))
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome

    @property
    def estoque_baixo(self):
        return self.estoque_atual <= self.estoque_minimo


class MotivoMovimentacao(models.TextChoices):
    VENDA = "VENDA", "Venda"
    CANCELAMENTO = "CANCELAMENTO", "Cancelamento de venda"
    AJUSTE = "AJUSTE", "Ajuste manual"
    ENTRADA = "ENTRADA", "Entrada de estoque"


class MovimentacaoEstoque(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name="movimentacoes")
    quantidade = models.DecimalField(max_digits=12, decimal_places=3)
    motivo = models.CharField(max_length=20, choices=MotivoMovimentacao.choices)
    observacao = models.CharField(max_length=255, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
