from decimal import Decimal

from django.conf import settings
from django.db import models


class FormaPagamento(models.TextChoices):
    DINHEIRO = "DINHEIRO", "Dinheiro"
    PIX = "PIX", "Pix"
    DEBITO = "DEBITO", "Débito"
    CREDITO = "CREDITO", "Crédito"
    FIADO = "FIADO", "Fiado"


class StatusVenda(models.TextChoices):
    ATIVA = "ATIVA", "Ativa"
    CANCELADA = "CANCELADA", "Cancelada"


class StatusFiado(models.TextChoices):
    PENDENTE = "PENDENTE", "Pendente"
    NOTIFICADO = "NOTIFICADO", "Notificado"
    EM_ATRASO = "EM_ATRASO", "Em atraso"
    PAGO = "PAGO", "Pago"


class Venda(models.Model):
    numero = models.PositiveIntegerField(unique=True, editable=False)
    cliente = models.ForeignKey(
        "clientes.Cliente", on_delete=models.SET_NULL, null=True, blank=True, related_name="vendas"
    )
    funcionario = models.ForeignKey(
        "funcionarios.Funcionario", on_delete=models.PROTECT, related_name="vendas"
    )
    forma_pagamento = models.CharField(max_length=10, choices=FormaPagamento.choices)
    status = models.CharField(max_length=12, choices=StatusVenda.choices, default=StatusVenda.ATIVA)
    status_fiado = models.CharField(
        max_length=12, choices=StatusFiado.choices, blank=True, null=True
    )
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    desconto = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    nota_emitida = models.BooleanField(default=False)
    motivo_cancelamento = models.CharField(max_length=255, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    vencimento_fiado = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-criado_em"]

    def __str__(self):
        return f"Venda #{self.numero}"


class ItemVenda(models.Model):
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name="itens")
    produto = models.ForeignKey("produtos.Produto", on_delete=models.PROTECT)
    quantidade = models.DecimalField(max_digits=12, decimal_places=3)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ["id"]


class Caixa(models.Model):
    funcionario = models.ForeignKey(
        "funcionarios.Funcionario", on_delete=models.PROTECT, related_name="caixas"
    )
    valor_abertura = models.DecimalField(max_digits=12, decimal_places=2)
    valor_fechamento = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    aberto_em = models.DateTimeField(auto_now_add=True)
    fechado_em = models.DateTimeField(null=True, blank=True)
    aberto = models.BooleanField(default=True)

    class Meta:
        ordering = ["-aberto_em"]


class CanalNotificacao(models.TextChoices):
    EMAIL = "EMAIL", "E-mail"
    WHATSAPP = "WHATSAPP", "WhatsApp"


class Notificacao(models.Model):
    cliente = models.ForeignKey("clientes.Cliente", on_delete=models.CASCADE, related_name="notificacoes")
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name="notificacoes", null=True, blank=True)
    canal = models.CharField(max_length=10, choices=CanalNotificacao.choices)
    mensagem = models.TextField()
    enviada_em = models.DateTimeField(auto_now_add=True)
    sucesso = models.BooleanField(default=True)

    class Meta:
        ordering = ["-enviada_em"]
