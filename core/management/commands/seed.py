"""Popula o SQLite com dados realistas para desenvolvimento e demonstração."""

import random
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from clientes.models import Cliente
from funcionarios.models import (
    Ausencia,
    Cargo,
    Funcionario,
    RegistroPonto,
    TipoAusencia,
    TipoRegistroPonto,
)
from produtos.models import Categoria, Produto, UnidadeMedida
from vendas.models import (
    CanalNotificacao,
    FormaPagamento,
    ItemVenda,
    Notificacao,
    StatusFiado,
    StatusVenda,
    Venda,
)

User = get_user_model()

FORMAS = [
    FormaPagamento.DINHEIRO,
    FormaPagamento.PIX,
    FormaPagamento.DEBITO,
    FormaPagamento.CREDITO,
    FormaPagamento.FIADO,
]


class Command(BaseCommand):
    help = "Popula o banco com dados de demonstração (dados reais no SQLite)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--if-empty",
            action="store_true",
            help="Executa o seed apenas se o banco estiver vazio (não apaga dados existentes).",
        )

    def handle(self, *args, **options):
        if options.get("if_empty"):
            has_data = any(
                model.objects.exists()
                for model in (User, Produto, Categoria, Cliente, Funcionario, Venda)
            )
            if has_data:
                self.stdout.write(
                    self.style.WARNING(
                        "Seed ignorado: banco já possui dados. "
                        "Use sem --if-empty para recriar tudo."
                    )
                )
                return

        self.stdout.write("Recriando dados de demonstração...")

        Notificacao.objects.all().delete()
        ItemVenda.objects.all().delete()
        Venda.objects.all().delete()
        Ausencia.objects.all().delete()
        RegistroPonto.objects.all().delete()
        Produto.objects.all().delete()
        Categoria.objects.all().delete()
        Cliente.objects.all().delete()
        Funcionario.objects.all().delete()
        User.objects.all().delete()

        admin = User.objects.create_user(
            username="admin",
            email="admin@paofresquim.com.br",
            password="admin123",
            first_name="Sr.",
            last_name="Quim",
            perfil="ADMIN",
            is_staff=True,
            is_superuser=True,
        )
        admin.loja = "Loja Centro"
        admin.save()

        ana = User.objects.create_user(
            username="ana.martins",
            email="ana@paofresquim.com.br",
            password="ana123",
            first_name="Ana",
            last_name="Martins",
            perfil="ATENDENTE",
        )
        ana.loja = "Loja Centro"
        ana.save()

        func_ana = Funcionario.objects.create(
            usuario=ana,
            nome="Ana Martins",
            cargo=Cargo.ATENDENTE,
            telefone="(11) 98765-4321",
            data_admissao=date(2021, 3, 15),
        )

        carlos = Funcionario.objects.create(
            nome="Carlos Eduardo Aragão",
            cargo=Cargo.PADEIRO,
            telefone="(11) 97462-1108",
            endereco="Rua Padre Marchetti, 84 — Mooca, São Paulo / SP",
            contato_emergencia="Helena Aragão (esposa) · (11) 99812-4471",
            data_admissao=date(2019, 3, 4),
            em_ferias_ate=date(2026, 5, 19),
        )

        Funcionario.objects.create(
            nome="Maria Oliveira",
            cargo=Cargo.ATENDENTE,
            telefone="(11) 99111-2233",
            data_admissao=date(2022, 8, 10),
        )

        Ausencia.objects.create(
            funcionario=carlos,
            tipo=TipoAusencia.FERIAS,
            titulo="Férias",
            data_inicio=date(2026, 5, 1),
            data_fim=date(2026, 5, 19),
            nome_arquivo="férias programadas",
        )

        hoje = timezone.now().date()
        for i, (entrada, saida) in enumerate(
            [(time(4, 58), time(12, 2)), (time(5, 1), time(12, 5)), (time(4, 55), time(11, 58))]
        ):
            d = hoje - timedelta(days=i + 1)
            RegistroPonto.objects.create(funcionario=carlos, data=d, tipo=TipoRegistroPonto.ENTRADA, hora=entrada)
            RegistroPonto.objects.create(funcionario=carlos, data=d, tipo=TipoRegistroPonto.SAIDA, hora=saida)

        categorias = {
            "Pães": Categoria.objects.create(nome="Pães"),
            "Doces & Confeitaria": Categoria.objects.create(nome="Doces & Confeitaria"),
            "Bebidas": Categoria.objects.create(nome="Bebidas"),
            "Mercearia": Categoria.objects.create(nome="Mercearia"),
        }

        produtos_cfg = [
            ("Pão Francês", "7891000100103", "Pães", "0.75", UnidadeMedida.PESO, "120", "3"),
            ("Pão de Queijo", "7891000600605", "Pães", "0.80", UnidadeMedida.PESO, "80", "2"),
            ("Rosca Grande", "7891000700706", "Pães", "12.90", UnidadeMedida.UNIDADE, "25", "5"),
            ("Biscoito de Polvilho", "7891000800807", "Pães", "28.00", UnidadeMedida.PESO, "15", "3"),
            ("Sonho Doce de Leite", "7891000200201", "Doces & Confeitaria", "6.50", UnidadeMedida.UNIDADE, "80", "10"),
            ("Leite Integral 1L", "7891000300302", "Bebidas", "5.90", UnidadeMedida.UNIDADE, "60", "5"),
            ("Café Pilão 250g", "7891000400403", "Mercearia", "14.80", UnidadeMedida.UNIDADE, "40", "5"),
            ("Queijo Minas", "7891000500504", "Mercearia", "49.90", UnidadeMedida.PESO, "20", "1"),
        ]
        produtos = []
        for nome, cod, cat_nome, preco, un, est, minimo in produtos_cfg:
            p = Produto.objects.create(
                nome=nome,
                codigo_barras=cod,
                categoria=categorias[cat_nome],
                preco_venda=Decimal(preco),
                unidade=un,
                estoque_atual=Decimal(est),
                estoque_minimo=Decimal(minimo),
            )
            produtos.append(p)

        joao = Cliente.objects.create(
            nome="João Pereira da Silva",
            cpf="472.103.882-90",
            telefone="(11) 98421-7733",
            email="joao.pereira@email.com",
            endereco="Rua das Acácias, 218 — Centro, São Paulo / SP",
            negativado=True,
            score_serasa=312,
            restricoes_serasa=2,
            ultima_consulta_serasa=timezone.now(),
            saldo_devedor=Decimal("40.30"),
            cliente_desde=date(2024, 2, 1),
        )

        maria = Cliente.objects.create(
            nome="Maria Silva",
            cpf="529.441.220-87",
            telefone="(11) 99123-4567",
            negativado=False,
            score_serasa=780,
            cliente_desde=date(2023, 6, 1),
        )

        pedro = Cliente.objects.create(
            nome="Pedro Henrique Costa",
            cpf="321.654.987-00",
            telefone="(11) 97777-8899",
            negativado=False,
            score_serasa=820,
            cliente_desde=date(2025, 1, 15),
        )

        agora = timezone.now()
        numero = 1800
        funcionarios = [func_ana]

        for dia_offset in range(14, -1, -1):
            dia = agora.date() - timedelta(days=dia_offset)
            vendas_no_dia = random.randint(4, 12) if dia_offset > 0 else random.randint(6, 14)

            for _ in range(vendas_no_dia):
                numero += 1
                forma = random.choice(FORMAS)
                cliente = None
                status_fiado = None
                if forma == FormaPagamento.FIADO:
                    cliente = random.choice([maria, pedro, joao])
                    if cliente.negativado:
                        forma = FormaPagamento.PIX
                        cliente = None
                    else:
                        status_fiado = StatusFiado.PENDENTE
                        if dia_offset > 7:
                            status_fiado = random.choice(
                                [StatusFiado.NOTIFICADO, StatusFiado.EM_ATRASO]
                            )

                hora_venda = time(random.randint(6, 18), random.randint(0, 59))
                criado = timezone.make_aware(datetime.combine(dia, hora_venda))

                p1 = random.choice(produtos)
                qtd = Decimal("0.420") if p1.unidade == UnidadeMedida.PESO else Decimal(str(random.randint(1, 4)))
                sub1 = (qtd * p1.preco_venda).quantize(Decimal("0.01"))

                p2 = random.choice(produtos)
                qtd2 = Decimal("1") if p2.unidade == UnidadeMedida.UNIDADE else Decimal("0.350")
                sub2 = (qtd2 * p2.preco_venda).quantize(Decimal("0.01"))

                total = sub1 + sub2

                venda = Venda.objects.create(
                    numero=numero,
                    cliente=cliente,
                    funcionario=random.choice(funcionarios),
                    forma_pagamento=forma,
                    subtotal=total,
                    total=total,
                    status_fiado=status_fiado,
                    criado_em=criado,
                    vencimento_fiado=dia + timedelta(days=30) if forma == FormaPagamento.FIADO else None,
                )
                ItemVenda.objects.create(
                    venda=venda, produto=p1, quantidade=qtd, preco_unitario=p1.preco_venda, subtotal=sub1
                )
                ItemVenda.objects.create(
                    venda=venda, produto=p2, quantidade=qtd2, preco_unitario=p2.preco_venda, subtotal=sub2
                )

                if forma == FormaPagamento.FIADO and cliente and status_fiado != StatusFiado.PAGO:
                    cliente.saldo_devedor += total
                    if status_fiado in (StatusFiado.NOTIFICADO, StatusFiado.EM_ATRASO):
                        Notificacao.objects.create(
                            cliente=cliente,
                            venda=venda,
                            canal=CanalNotificacao.WHATSAPP,
                            mensagem="Lembrete de fiado em aberto na Padaria Pão FresQUIM.",
                            enviada_em=criado + timedelta(days=5),
                        )

        for c in [maria, pedro, joao]:
            c.save(update_fields=["saldo_devedor"])

        pao = produtos[0]
        pao.estoque_atual = Decimal("3.2")
        pao.save(update_fields=["estoque_atual"])

        self.stdout.write(self.style.SUCCESS("Seed concluído com dados no banco SQLite."))
        self.stdout.write(f"  Produtos: {Produto.objects.count()}")
        self.stdout.write(f"  Clientes: {Cliente.objects.count()}")
        self.stdout.write(f"  Funcionários: {Funcionario.objects.count()}")
        self.stdout.write(f"  Vendas: {Venda.objects.count()}")
        self.stdout.write("Login: ana.martins / ana123  |  admin / admin123")
