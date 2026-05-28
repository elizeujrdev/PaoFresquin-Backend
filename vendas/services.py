from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from clientes.models import Cliente
from produtos.models import MotivoMovimentacao, MovimentacaoEstoque, Produto
from vendas.models import FormaPagamento, ItemVenda, StatusFiado, StatusVenda, Venda


class RegraNegocioException(ValidationError):
    pass


def _proximo_numero_venda():
    ultima = Venda.objects.order_by("-numero").values_list("numero", flat=True).first()
    return (ultima or 0) + 1


@transaction.atomic
def criar_venda(*, funcionario, itens_data, forma_pagamento, cliente=None, desconto=Decimal("0")):
    if forma_pagamento == FormaPagamento.FIADO:
        if not cliente:
            raise RegraNegocioException("Venda fiado exige um cliente cadastrado.")
        if not cliente.pode_fiado():
            raise RegraNegocioException("Cliente bloqueado para fiado.")

    subtotal = Decimal("0")
    itens_preparados = []

    for item in itens_data:
        produto = Produto.objects.select_for_update().get(pk=item["produto_id"], ativo=True)
        qtd = Decimal(str(item["quantidade"]))
        if produto.estoque_atual < qtd:
            raise RegraNegocioException(f"Estoque insuficiente para {produto.nome}.")
        preco = Decimal(str(item.get("preco_unitario", produto.preco_venda)))
        item_sub = (qtd * preco).quantize(Decimal("0.01"))
        subtotal += item_sub
        itens_preparados.append((produto, qtd, preco, item_sub))

    total = (subtotal - Decimal(str(desconto))).quantize(Decimal("0.01"))

    venda = Venda.objects.create(
        numero=_proximo_numero_venda(),
        cliente=cliente,
        funcionario=funcionario,
        forma_pagamento=forma_pagamento,
        subtotal=subtotal,
        desconto=desconto,
        total=total,
        status_fiado=StatusFiado.PENDENTE if forma_pagamento == FormaPagamento.FIADO else None,
        vencimento_fiado=(timezone.now().date() + timedelta(days=30))
        if forma_pagamento == FormaPagamento.FIADO
        else None,
    )

    for produto, qtd, preco, item_sub in itens_preparados:
        ItemVenda.objects.create(
            venda=venda,
            produto=produto,
            quantidade=qtd,
            preco_unitario=preco,
            subtotal=item_sub,
        )
        produto.estoque_atual -= qtd
        produto.save(update_fields=["estoque_atual"])
        MovimentacaoEstoque.objects.create(
            produto=produto,
            quantidade=-qtd,
            motivo=MotivoMovimentacao.VENDA,
            observacao=f"Venda #{venda.numero}",
        )

    if forma_pagamento == FormaPagamento.FIADO and cliente:
        cliente.saldo_devedor += total
        cliente.save(update_fields=["saldo_devedor"])

    return venda


@transaction.atomic
def cancelar_venda(venda: Venda, motivo: str = ""):
    if venda.status == StatusVenda.CANCELADA:
        raise RegraNegocioException("Venda já está cancelada.")

    for item in venda.itens.select_related("produto"):
        produto = Produto.objects.select_for_update().get(pk=item.produto_id)
        produto.estoque_atual += item.quantidade
        produto.save(update_fields=["estoque_atual"])
        MovimentacaoEstoque.objects.create(
            produto=produto,
            quantidade=item.quantidade,
            motivo=MotivoMovimentacao.CANCELAMENTO,
            observacao=f"Cancelamento venda #{venda.numero}",
        )

    if venda.forma_pagamento == FormaPagamento.FIADO and venda.cliente:
        if venda.status_fiado != StatusFiado.PAGO:
            venda.cliente.saldo_devedor = max(
                Decimal("0"), venda.cliente.saldo_devedor - venda.total
            )
            venda.cliente.save(update_fields=["saldo_devedor"])

    venda.status = StatusVenda.CANCELADA
    venda.motivo_cancelamento = motivo
    venda.save(update_fields=["status", "motivo_cancelamento", "atualizado_em"])
    return venda
