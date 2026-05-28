from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import PodeCancelarVenda, PodeVendas
from vendas.models import StatusVenda, Venda
from vendas.serializers import VendaCreateSerializer, VendaListSerializer, VendaSerializer
from vendas.services import cancelar_venda


class VendaViewSet(viewsets.ModelViewSet):
    queryset = Venda.objects.select_related("cliente", "funcionario").prefetch_related("itens__produto")
    http_method_names = ["get", "post", "head", "options"]

    def get_serializer_class(self):
        if self.action == "list":
            return VendaListSerializer
        if self.action == "create":
            return VendaCreateSerializer
        return VendaSerializer

    def get_permissions(self):
        if self.action == "create":
            return [PodeVendas()]
        if self.action == "cancelar":
            return [PodeCancelarVenda()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = VendaCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        venda = serializer.save()
        return Response(VendaSerializer(venda).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def cancelar(self, request, pk=None):
        venda = self.get_object()
        cancelar_venda(venda, request.data.get("motivo", ""))
        return Response(VendaSerializer(venda).data)

    @action(detail=False, methods=["get"])
    def recentes(self, request):
        vendas = self.get_queryset().filter(status=StatusVenda.ATIVA).order_by("-criado_em")[:10]
        return Response(VendaListSerializer(vendas, many=True).data)

    @action(detail=False, methods=["get"])
    def proxima(self, request):
        from vendas.services import _proximo_numero_venda

        return Response({"numero": _proximo_numero_venda()})

    @action(detail=True, methods=["post"])
    def emitir_nota(self, request, pk=None):
        venda = self.get_object()
        venda.nota_emitida = True
        venda.save(update_fields=["nota_emitida"])
        return Response({"nota_emitida": True})
