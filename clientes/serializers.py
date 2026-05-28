from datetime import date

from rest_framework import serializers

from clientes.models import Cliente
from core.services.serasa import consultar_cpf
from vendas.models import FormaPagamento, StatusFiado, StatusVenda, Venda


class FiadoHistoricoSerializer(serializers.ModelSerializer):
    status_label = serializers.SerializerMethodField()
    descricao = serializers.SerializerMethodField()

    class Meta:
        model = Venda
        fields = ["id", "numero", "criado_em", "total", "status_fiado", "status_label", "descricao"]

    def get_status_label(self, obj):
        if obj.status_fiado == StatusFiado.PAGO:
            return "pago"
        return "aberto"

    def get_descricao(self, obj):
        itens = list(obj.itens.select_related("produto")[:3])
        if not itens:
            return f"Venda #{obj.numero}"
        nomes = [i.produto.nome for i in itens]
        return ", ".join(nomes) if len(itens) <= 2 else f"{len(obj.itens.all())} itens"


class ClienteSerializer(serializers.ModelSerializer):
    historico_fiado = serializers.SerializerMethodField()
    pode_salvar_fiado = serializers.SerializerMethodField()

    class Meta:
        model = Cliente
        fields = [
            "id",
            "nome",
            "cpf",
            "telefone",
            "email",
            "endereco",
            "negativado",
            "score_serasa",
            "restricoes_serasa",
            "ultima_consulta_serasa",
            "saldo_devedor",
            "ativo",
            "cliente_desde",
            "historico_fiado",
            "pode_salvar_fiado",
        ]
        read_only_fields = [
            "negativado",
            "score_serasa",
            "restricoes_serasa",
            "ultima_consulta_serasa",
            "saldo_devedor",
        ]

    def get_historico_fiado(self, obj):
        vendas = (
            obj.vendas.filter(forma_pagamento=FormaPagamento.FIADO, status=StatusVenda.ATIVA)
            .prefetch_related("itens__produto")
            .order_by("-criado_em")[:10]
        )
        return FiadoHistoricoSerializer(vendas, many=True).data

    def get_pode_salvar_fiado(self, obj):
        return obj.pode_fiado()

    def create(self, validated_data):
        resultado = consultar_cpf(validated_data["cpf"])
        if resultado.negativado:
            raise serializers.ValidationError(
                {
                    "cpf": "Nome negativado na consulta Serasa. Cadastro bloqueado conforme política da padaria."
                }
            )
        validated_data["negativado"] = False
        validated_data["score_serasa"] = resultado.score
        validated_data["restricoes_serasa"] = resultado.restricoes
        validated_data["ultima_consulta_serasa"] = resultado.consultado_em
        validated_data.setdefault("cliente_desde", date.today())
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "cpf" in validated_data and validated_data["cpf"] != instance.cpf:
            resultado = consultar_cpf(validated_data["cpf"])
            if resultado.negativado:
                raise serializers.ValidationError({"cpf": "CPF negativado no Serasa."})
            instance.score_serasa = resultado.score
            instance.restricoes_serasa = resultado.restricoes
            instance.ultima_consulta_serasa = resultado.consultado_em
            instance.negativado = resultado.negativado
        return super().update(instance, validated_data)
