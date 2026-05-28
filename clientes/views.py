from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from clientes.models import Cliente
from clientes.serializers import ClienteSerializer
from core.services.serasa import consultar_cpf


class ClienteViewSet(viewsets.ModelViewSet):
    serializer_class = ClienteSerializer
    search_fields = ["nome", "cpf", "telefone"]

    def get_queryset(self):
        qs = Cliente.objects.all()
        if self.action == "list" and not self.request.query_params.get("todos"):
            qs = qs.filter(ativo=True)
        return qs

    def perform_destroy(self, instance):
        instance.ativo = False
        instance.save(update_fields=["ativo"])

    @action(detail=False, methods=["get"], url_path="consulta-serasa/(?P<cpf>[^/.]+)")
    def consulta_serasa(self, request, cpf=None):
        resultado = consultar_cpf(cpf)
        return Response(
            {
                "cpf": resultado.cpf,
                "negativado": resultado.negativado,
                "score": resultado.score,
                "restricoes": resultado.restricoes,
                "consultado_em": resultado.consultado_em,
            }
        )

    @action(detail=True, methods=["post"])
    def reconsultar_serasa(self, request, pk=None):
        cliente = self.get_object()
        resultado = consultar_cpf(cliente.cpf)
        cliente.negativado = resultado.negativado
        cliente.score_serasa = resultado.score
        cliente.restricoes_serasa = resultado.restricoes
        cliente.ultima_consulta_serasa = timezone.now()
        cliente.save()
        return Response(ClienteSerializer(cliente).data)

    @action(detail=False, methods=["get"])
    def fiados_vencidos(self, request):
        from vendas.models import FormaPagamento, StatusFiado, StatusVenda

        clientes = Cliente.objects.filter(
            vendas__forma_pagamento=FormaPagamento.FIADO,
            vendas__status=StatusVenda.ATIVA,
            vendas__status_fiado__in=[StatusFiado.EM_ATRASO, StatusFiado.NOTIFICADO],
        ).distinct()
        return Response(ClienteSerializer(clientes, many=True).data)
