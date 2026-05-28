from rest_framework import serializers

from produtos.models import Categoria, Produto


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nome", "ativo"]


class ProdutoSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.CharField(source="categoria.nome", read_only=True)
    estoque_baixo = serializers.BooleanField(read_only=True)

    class Meta:
        model = Produto
        fields = [
            "id",
            "nome",
            "codigo_barras",
            "categoria",
            "categoria_nome",
            "preco_venda",
            "preco_custo",
            "unidade",
            "descricao",
            "estoque_atual",
            "estoque_minimo",
            "estoque_baixo",
            "ativo",
        ]

    def validate_codigo_barras(self, value):
        if not value:
            return value
        qs = Produto.objects.filter(codigo_barras=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Código de barras já cadastrado.")
        return value
