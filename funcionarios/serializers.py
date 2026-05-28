from rest_framework import serializers

from funcionarios.models import Ausencia, Funcionario, RegistroPonto


class RegistroPontoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroPonto
        fields = ["id", "tipo", "data", "hora", "origem"]


class AusenciaSerializer(serializers.ModelSerializer):
    arquivo_url = serializers.SerializerMethodField()

    class Meta:
        model = Ausencia
        fields = [
            "id",
            "tipo",
            "titulo",
            "data_inicio",
            "data_fim",
            "arquivo_url",
            "nome_arquivo",
            "observacao",
        ]

    def get_arquivo_url(self, obj):
        if obj.arquivo:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.arquivo.url)
            return obj.arquivo.url
        return None


class FuncionarioSerializer(serializers.ModelSerializer):
    iniciais = serializers.CharField(read_only=True)
    cargo_label = serializers.CharField(source="get_cargo_display", read_only=True)
    pontos = serializers.SerializerMethodField()
    pontos_resumo = serializers.SerializerMethodField()
    ausencias = AusenciaSerializer(many=True, read_only=True)

    class Meta:
        model = Funcionario
        fields = [
            "id",
            "nome",
            "cargo",
            "cargo_label",
            "telefone",
            "endereco",
            "contato_emergencia",
            "data_admissao",
            "ativo",
            "em_ferias_ate",
            "iniciais",
            "pontos",
            "pontos_resumo",
            "ausencias",
            "usuario",
        ]

    def get_pontos(self, obj):
        from datetime import timedelta
        from django.utils import timezone

        inicio = timezone.now().date() - timedelta(days=7)
        registros = obj.pontos.filter(data__gte=inicio).order_by("data", "hora")
        return RegistroPontoSerializer(registros, many=True).data

    def get_pontos_resumo(self, obj):
        from datetime import timedelta
        from django.utils import timezone

        hoje = timezone.now().date()
        inicio = hoje - timedelta(days=6)
        dias = []
        for i in range(7):
            d = inicio + timedelta(days=i)
            regs = list(obj.pontos.filter(data=d).order_by("hora"))
            entrada = next((r.hora.strftime("%H:%M") for r in regs if r.tipo == "ENTRADA"), None)
            saida = next((r.hora.strftime("%H:%M") for r in regs if r.tipo == "SAIDA"), None)
            obs = None
            if obj.em_ferias_ate and d <= obj.em_ferias_ate and d >= (obj.em_ferias_ate - timedelta(days=30)):
                ausencia = obj.ausencias.filter(data_inicio__lte=d, data_fim__gte=d, tipo="FERIAS").first()
                if ausencia:
                    obs = "férias"
            total = None
            if entrada and saida:
                from datetime import datetime as dt

                e = dt.combine(d, dt.strptime(entrada, "%H:%M").time())
                s = dt.combine(d, dt.strptime(saida, "%H:%M").time())
                mins = int((s - e).total_seconds() // 60)
                total = f"{mins // 60}h{mins % 60:02d}"
            dias.append(
                {
                    "data": d.strftime("%a %d/%m").lower(),
                    "entrada": entrada or "—",
                    "saida": saida or "—",
                    "total": total or (obs or "—"),
                    "obs": obs,
                }
            )
        return dias
