from datetime import datetime, timedelta
from decimal import Decimal

from django.db.models import Count, F, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import PodeRelatorios
from clientes.models import Cliente
from core.services.cameras import listar_cameras
from funcionarios.models import Funcionario
from produtos.models import Produto
from vendas.models import FormaPagamento, StatusFiado, StatusVenda, Venda


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        hoje = timezone.now().date()
        vendas_hoje = Venda.objects.filter(
            criado_em__date=hoje, status=StatusVenda.ATIVA
        )
        total_hoje = vendas_hoje.aggregate(t=Sum("total"))["t"] or Decimal("0")
        count_hoje = vendas_hoje.count()

        fiados_vencidos = Venda.objects.filter(
            forma_pagamento=FormaPagamento.FIADO,
            status=StatusVenda.ATIVA,
            status_fiado__in=[StatusFiado.EM_ATRASO, StatusFiado.NOTIFICADO],
        ).count()

        fiado_aberto = (
            Venda.objects.filter(
                forma_pagamento=FormaPagamento.FIADO,
                status=StatusVenda.ATIVA,
            )
            .exclude(status_fiado=StatusFiado.PAGO)
            .aggregate(t=Sum("total"))["t"]
            or Decimal("0")
        )

        estoque_baixo = Produto.objects.filter(
            ativo=True, estoque_atual__lte=F("estoque_minimo")
        ).count()

        primeiro_produto_baixo = (
            Produto.objects.filter(ativo=True, estoque_atual__lte=F("estoque_minimo"))
            .first()
        )

        funcionario_ferias = Funcionario.objects.filter(
            em_ferias_ate__gte=hoje, ativo=True
        ).first()

        hora = timezone.now().hour
        saudacao = "Bom dia" if hora < 12 else "Boa tarde" if hora < 18 else "Boa noite"

        return Response(
            {
                "saudacao": saudacao,
                "vendas_hoje": count_hoje,
                "total_hoje": str(total_hoje),
                "fiados_vencidos": fiados_vencidos,
                "fiado_aberto": str(fiado_aberto),
                "cameras_online": True,
                "estoque_baixo": estoque_baixo,
                "produto_estoque_baixo": (
                    {
                        "nome": primeiro_produto_baixo.nome,
                        "estoque": str(primeiro_produto_baixo.estoque_atual),
                    }
                    if primeiro_produto_baixo
                    else None
                ),
                "funcionario_retorno": (
                    {
                        "nome": funcionario_ferias.nome.split()[0],
                        "cargo": funcionario_ferias.get_cargo_display(),
                        "data": funcionario_ferias.em_ferias_ate.strftime("%d/%m"),
                    }
                    if funcionario_ferias
                    else None
                ),
            }
        )


class AvisosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        avisos = []
        fiados = Venda.objects.filter(
            forma_pagamento=FormaPagamento.FIADO,
            status=StatusVenda.ATIVA,
            status_fiado__in=[StatusFiado.EM_ATRASO, StatusFiado.NOTIFICADO],
        ).count()
        if fiados:
            from vendas.models import Notificacao

            ultima = (
                Notificacao.objects.order_by("-enviada_em").values_list("enviada_em", flat=True).first()
            )
            sub = (
                f"Última notificação: {ultima.strftime('%d/%m/%Y')}"
                if ultima
                else "Notificações pendentes de envio"
            )
            avisos.append(
                {
                    "tipo": "danger",
                    "titulo": f"{fiados} clientes com fiado vencido",
                    "subtitulo": sub,
                }
            )

        p = Produto.objects.filter(ativo=True, estoque_atual__lte=F("estoque_minimo")).first()
        if p:
            avisos.append(
                {
                    "tipo": "warning",
                    "titulo": f"{p.nome} próximo do mínimo",
                    "subtitulo": f"{p.estoque_atual} {'kg' if p.unidade == 'PESO' else 'un'} restantes",
                }
            )

        func = Funcionario.objects.filter(em_ferias_ate__gte=timezone.now().date()).first()
        if func:
            avisos.append(
                {
                    "tipo": "muted",
                    "titulo": f"{func.nome.split()[0]} retorna de férias",
                    "subtitulo": f"{func.get_cargo_display()}",
                }
            )

        return Response(avisos)


class CamerasView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cameras = listar_cameras()
        return Response(
            {
                "cameras": cameras,
                "total": len(cameras),
                "sistema_ativo": True,
            }
        )


class RelatoriosVendasView(APIView):
    permission_classes = [PodeRelatorios]

    def get(self, request):
        import time

        inicio_perf = time.perf_counter()

        data_inicio = request.query_params.get("data_inicio")
        data_fim = request.query_params.get("data_fim")
        produto_id = request.query_params.get("produto")
        funcionario_id = request.query_params.get("funcionario")

        hoje = timezone.now().date()
        if not data_fim:
            data_fim = hoje
        else:
            data_fim = datetime.strptime(data_fim, "%Y-%m-%d").date()
        if not data_inicio:
            data_inicio = data_fim - timedelta(days=9)
        else:
            data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d").date()

        vendas = Venda.objects.filter(
            status=StatusVenda.ATIVA,
            criado_em__date__gte=data_inicio,
            criado_em__date__lte=data_fim,
        )
        if funcionario_id:
            vendas = vendas.filter(funcionario_id=funcionario_id)

        total_vendido = vendas.aggregate(t=Sum("total"))["t"] or Decimal("0")
        count_vendas = vendas.count()
        ticket = (total_vendido / count_vendas).quantize(Decimal("0.01")) if count_vendas else Decimal("0")

        fiado_vendas = vendas.filter(forma_pagamento=FormaPagamento.FIADO)
        total_fiado = fiado_vendas.aggregate(t=Sum("total"))["t"] or Decimal("0")
        pct_fiado = float(total_fiado / total_vendido * 100) if total_vendido else 0

        em_aberto = (
            Venda.objects.filter(
                forma_pagamento=FormaPagamento.FIADO,
                status=StatusVenda.ATIVA,
            )
            .exclude(status_fiado=StatusFiado.PAGO)
            .aggregate(t=Sum("total"))["t"]
            or Decimal("0")
        )
        clientes_aberto = (
            Cliente.objects.filter(saldo_devedor__gt=0).count()
        )

        por_dia = (
            vendas.annotate(dia=TruncDate("criado_em"))
            .values("dia")
            .annotate(total=Sum("total"), qtd=Count("id"))
            .order_by("dia")
        )
        dias_labels = []
        dias_valores = []
        for row in por_dia:
            dias_labels.append(row["dia"].strftime("%a")[:3].lower())
            dias_valores.append(float(row["total"]))

        from vendas.models import ItemVenda

        itens_qs = ItemVenda.objects.filter(venda__in=vendas)
        if produto_id:
            itens_qs = itens_qs.filter(produto_id=produto_id)

        mais_vendidos = (
            itens_qs.values("produto__nome", "produto__unidade")
            .annotate(qtd=Sum("quantidade"))
            .order_by("-qtd")[:5]
        )
        top_produtos = []
        max_qtd = float(mais_vendidos[0]["qtd"]) if mais_vendidos else 1
        for item in mais_vendidos:
            qtd = float(item["qtd"])
            un = "kg" if item["produto__unidade"] == "PESO" else "un"
            top_produtos.append(
                {
                    "nome": item["produto__nome"],
                    "quantidade": qtd,
                    "unidade": un,
                    "percentual": round(qtd / max_qtd * 100) if max_qtd else 0,
                }
            )

        dias_periodo = (data_fim - data_inicio).days + 1
        inicio_anterior = data_inicio - timedelta(days=dias_periodo)
        fim_anterior = data_inicio - timedelta(days=1)
        vendas_anterior = Venda.objects.filter(
            status=StatusVenda.ATIVA,
            criado_em__date__gte=inicio_anterior,
            criado_em__date__lte=fim_anterior,
        )
        total_anterior = vendas_anterior.aggregate(t=Sum("total"))["t"] or Decimal("0")
        count_anterior = vendas_anterior.count()
        ticket_anterior = (
            (total_anterior / count_anterior).quantize(Decimal("0.01")) if count_anterior else Decimal("0")
        )
        variacao_pct = (
            float((total_vendido - total_anterior) / total_anterior * 100)
            if total_anterior
            else 0
        )
        variacao_ticket = ticket - ticket_anterior

        elapsed = time.perf_counter() - inicio_perf

        return Response(
            {
                "periodo": {
                    "inicio": data_inicio.isoformat(),
                    "fim": data_fim.isoformat(),
                },
                "total_vendas_periodo": count_vendas,
                "total_vendido": str(total_vendido),
                "ticket_medio": str(ticket),
                "vendas_fiado": str(total_fiado),
                "pct_fiado": round(pct_fiado, 1),
                "em_aberto": str(em_aberto),
                "clientes_em_aberto": clientes_aberto,
                "vendas_por_dia": {"labels": dias_labels, "valores": dias_valores},
                "mais_vendidos": top_produtos,
                "tempo_carregamento": round(elapsed, 2),
                "variacao_pct": round(variacao_pct, 1),
                "variacao_ticket": str(variacao_ticket.quantize(Decimal("0.01"))),
            }
        )


class RelatoriosEstoqueView(APIView):
    permission_classes = [PodeRelatorios]

    def get(self, request):
        produtos = Produto.objects.filter(ativo=True).select_related("categoria").order_by("nome")
        lista = [
            {
                "id": p.id,
                "nome": p.nome,
                "categoria": p.categoria.nome,
                "estoque_atual": str(p.estoque_atual),
                "estoque_minimo": str(p.estoque_minimo),
                "unidade": p.unidade,
                "estoque_baixo": p.estoque_baixo,
            }
            for p in produtos
        ]
        return Response(lista)


class InadimplenciaView(APIView):
    permission_classes = [PodeRelatorios]

    def get(self, request):
        from vendas.models import Notificacao

        vendas = (
            Venda.objects.filter(
                forma_pagamento=FormaPagamento.FIADO,
                status=StatusVenda.ATIVA,
            )
            .exclude(status_fiado=StatusFiado.PAGO)
            .select_related("cliente")
            .prefetch_related("itens__produto", "notificacoes")
        )
        lista = []
        for v in vendas:
            ultima_notif = v.notificacoes.order_by("-enviada_em").first()
            lista.append(
                {
                    "venda_id": v.id,
                    "numero": v.numero,
                    "cliente": v.cliente.nome if v.cliente else "",
                    "total": str(v.total),
                    "data_compra": v.criado_em.strftime("%d/%m/%Y"),
                    "status_fiado": v.status_fiado,
                    "ultima_notificacao": (
                        ultima_notif.enviada_em.strftime("%d/%m/%Y %H:%M")
                        if ultima_notif
                        else None
                    ),
                    "itens": [
                        {"produto": i.produto.nome, "qtd": str(i.quantidade), "subtotal": str(i.subtotal)}
                        for i in v.itens.all()
                    ],
                }
            )
        return Response(lista)
