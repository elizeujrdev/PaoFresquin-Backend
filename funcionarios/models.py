from django.conf import settings
from django.db import models


class Cargo(models.TextChoices):
    PADEIRO = "PADEIRO", "Padeiro"
    ATENDENTE = "ATENDENTE", "Atendente"
    GERENTE = "GERENTE", "Gerente"
    OUTRO = "OUTRO", "Outro"


class Funcionario(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="funcionario"
    )
    nome = models.CharField(max_length=200)
    cargo = models.CharField(max_length=20, choices=Cargo.choices)
    telefone = models.CharField(max_length=20, blank=True)
    endereco = models.CharField(max_length=300, blank=True)
    contato_emergencia = models.CharField(max_length=200, blank=True)
    data_admissao = models.DateField()
    ativo = models.BooleanField(default=True)
    em_ferias_ate = models.DateField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome

    @property
    def iniciais(self):
        parts = self.nome.split()
        return "".join(p[0].upper() for p in parts[:2])


class TipoRegistroPonto(models.TextChoices):
    ENTRADA = "ENTRADA", "Entrada"
    SAIDA = "SAIDA", "Saída"


class RegistroPonto(models.Model):
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name="pontos")
    tipo = models.CharField(max_length=10, choices=TipoRegistroPonto.choices)
    data = models.DateField()
    hora = models.TimeField()
    origem = models.CharField(max_length=30, default="manual")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-data", "-hora"]


class TipoAusencia(models.TextChoices):
    ATESTADO = "ATESTADO", "Atestado médico"
    LICENCA = "LICENCA", "Licença"
    FERIAS = "FERIAS", "Férias"
    OUTRO = "OUTRO", "Outro"


class Ausencia(models.Model):
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name="ausencias")
    tipo = models.CharField(max_length=12, choices=TipoAusencia.choices)
    titulo = models.CharField(max_length=120)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    arquivo = models.FileField(upload_to="atestados/", blank=True, null=True)
    nome_arquivo = models.CharField(max_length=200, blank=True)
    observacao = models.CharField(max_length=255, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-data_inicio"]
