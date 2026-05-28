from rest_framework import parsers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import PodeFuncionarios
from funcionarios.models import Ausencia, Funcionario, RegistroPonto
from funcionarios.serializers import AusenciaSerializer, FuncionarioSerializer, RegistroPontoSerializer


class FuncionarioViewSet(viewsets.ModelViewSet):
    serializer_class = FuncionarioSerializer
    search_fields = ["nome", "cargo"]

    def get_queryset(self):
        qs = Funcionario.objects.prefetch_related("pontos", "ausencias")
        if self.action == "list" and not self.request.query_params.get("todos"):
            qs = qs.filter(ativo=True)
        return qs

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy", "desligar"):
            return [PodeFuncionarios()]
        return super().get_permissions()

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def perform_destroy(self, instance):
        instance.ativo = False
        instance.save(update_fields=["ativo"])

    @action(detail=True, methods=["post"])
    def desligar(self, request, pk=None):
        funcionario = self.get_object()
        funcionario.ativo = False
        funcionario.save(update_fields=["ativo"])
        return Response(FuncionarioSerializer(funcionario, context={"request": request}).data)

    @action(detail=True, methods=["get", "post"])
    def pontos(self, request, pk=None):
        funcionario = self.get_object()
        if request.method == "GET":
            registros = funcionario.pontos.all()[:30]
            return Response(RegistroPontoSerializer(registros, many=True).data)
        serializer = RegistroPontoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        RegistroPonto.objects.create(funcionario=funcionario, **serializer.validated_data)
        return Response(serializer.data, status=201)

    @action(
        detail=True,
        methods=["get", "post"],
        parser_classes=[parsers.MultiPartParser, parsers.FormParser],
    )
    def ausencias(self, request, pk=None):
        funcionario = self.get_object()
        if request.method == "GET":
            return Response(
                AusenciaSerializer(
                    funcionario.ausencias.all(), many=True, context={"request": request}
                ).data
            )
        data = request.data.copy()
        arquivo = request.FILES.get("arquivo")
        ausencia = Ausencia.objects.create(
            funcionario=funcionario,
            tipo=data.get("tipo", "ATESTADO"),
            titulo=data.get("titulo", ""),
            data_inicio=data["data_inicio"],
            data_fim=data["data_fim"],
            observacao=data.get("observacao", ""),
            arquivo=arquivo,
            nome_arquivo=arquivo.name if arquivo else data.get("nome_arquivo", ""),
        )
        return Response(
            AusenciaSerializer(ausencia, context={"request": request}).data,
            status=201,
        )
