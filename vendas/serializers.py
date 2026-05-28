from rest_framework import serializers

from clientes.models import Cliente
from funcionarios.models import Funcionario
from produtos.models import Produto
from core.datetime_br import format_time_br
from vendas.models import ItemVenda, Venda
from vendas.services import cancelar_venda, criar_venda


class ItemVendaSerializer(serializers.ModelSerializer):
    produto_nome = serializers.CharField(source="produto.nome", read_only=True)
    produto_unidade = serializers.CharField(source="produto.unidade", read_only=True)

    class Meta:
        model = ItemVenda
        fields = [
            "id",
            "produto",
            "produto_nome",
            "produto_unidade",
            "quantidade",
            "preco_unitario",
            "subtotal",
        ]


class VendaSerializer(serializers.ModelSerializer):
    itens = ItemVendaSerializer(many=True, read_only=True)
    cliente_nome = serializers.CharField(source="cliente.nome", read_only=True, allow_null=True)
    funcionario_nome = serializers.CharField(source="funcionario.nome", read_only=True)
    forma_pagamento_label = serializers.CharField(source="get_forma_pagamento_display", read_only=True)

    class Meta:
        model = Venda
        fields = [
            "id",
            "numero",
            "cliente",
            "cliente_nome",
            "funcionario",
            "funcionario_nome",
            "forma_pagamento",
            "forma_pagamento_label",
            "status",
            "status_fiado",
            "subtotal",
            "desconto",
            "total",
            "nota_emitida",
            "itens",
            "criado_em",
        ]


class ItemVendaCreateSerializer(serializers.Serializer):
    produto_id = serializers.IntegerField()
    quantidade = serializers.DecimalField(max_digits=12, decimal_places=3)
    preco_unitario = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)


class VendaCreateSerializer(serializers.Serializer):
    itens = ItemVendaCreateSerializer(many=True)
    forma_pagamento = serializers.ChoiceField(choices=["DINHEIRO", "PIX", "DEBITO", "CREDITO", "FIADO"])
    cliente_id = serializers.IntegerField(required=False, allow_null=True)
    desconto = serializers.DecimalField(max_digits=12, decimal_places=2, default=0)
    funcionario_id = serializers.IntegerField(required=False)

    def create(self, validated_data):
        request = self.context["request"]
        funcionario = None
        fid = validated_data.get("funcionario_id")
        if fid:
            try:
                funcionario = Funcionario.objects.get(pk=fid, ativo=True)
            except Funcionario.DoesNotExist:
                raise serializers.ValidationError(
                    {"funcionario_id": "Funcionário não encontrado ou inativo."}
                )
        elif hasattr(request.user, "funcionario"):
            funcionario = request.user.funcionario
        if not funcionario:
            funcionario = Funcionario.objects.filter(ativo=True).first()
        if not funcionario:
            raise serializers.ValidationError(
                "Cadastre um funcionário ativo para registrar vendas."
            )

        cliente = None
        if validated_data.get("cliente_id"):
            try:
                cliente = Cliente.objects.get(pk=validated_data["cliente_id"], ativo=True)
            except Cliente.DoesNotExist:
                raise serializers.ValidationError({"cliente_id": "Cliente não encontrado."})

        return criar_venda(
            funcionario=funcionario,
            itens_data=validated_data["itens"],
            forma_pagamento=validated_data["forma_pagamento"],
            cliente=cliente,
            desconto=validated_data.get("desconto", 0),
        )


class VendaListSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.SerializerMethodField()
    hora = serializers.SerializerMethodField()

    class Meta:
        model = Venda
        fields = ["id", "numero", "hora", "cliente_nome", "forma_pagamento", "total", "criado_em"]

    def get_cliente_nome(self, obj):
        return obj.cliente.nome if obj.cliente else "Consumidor"

    def get_hora(self, obj):
        return format_time_br(obj.criado_em)
