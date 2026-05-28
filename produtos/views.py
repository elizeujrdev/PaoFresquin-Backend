from django.db.models import F, Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import PodeVendas
from produtos.models import Categoria, Produto
from produtos.serializers import CategoriaSerializer, ProdutoSerializer


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.filter(ativo=True)
    serializer_class = CategoriaSerializer
    search_fields = ["nome"]


class ProdutoViewSet(viewsets.ModelViewSet):
    serializer_class = ProdutoSerializer
    search_fields = ["nome", "codigo_barras"]

    def get_queryset(self):
        qs = Produto.objects.select_related("categoria")
        if self.action == "list" and not self.request.query_params.get("todos"):
            qs = qs.filter(ativo=True)
        if self.action in ("list", "retrieve") and self.request.query_params.get("pdv"):
            return qs.filter(ativo=True)
        return qs

    def perform_destroy(self, instance):
        instance.ativo = False
        instance.save(update_fields=["ativo"])

    @action(detail=False, methods=["get"], url_path="por-codigo/(?P<codigo>[^/.]+)")
    def por_codigo(self, request, codigo=None):
        produto = Produto.objects.filter(ativo=True).filter(
            Q(codigo_barras=codigo) | Q(codigo_barras__startswith=codigo)
        ).first()
        if not produto:
            return Response({"detail": "Produto não encontrado."}, status=404)
        return Response(ProdutoSerializer(produto).data)

    @action(detail=False, methods=["get"])
    def alertas_estoque(self, request):
        produtos = Produto.objects.filter(
            ativo=True, estoque_atual__lte=F("estoque_minimo")
        )[:10]
        return Response(ProdutoSerializer(produtos, many=True).data)
