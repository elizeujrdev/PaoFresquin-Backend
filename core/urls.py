from django.urls import path

from core.views import (
    AvisosView,
    CamerasView,
    DashboardView,
    InadimplenciaView,
    RelatoriosEstoqueView,
    RelatoriosVendasView,
)

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("avisos/", AvisosView.as_view(), name="avisos"),
    path("cameras/", CamerasView.as_view(), name="cameras"),
    path("relatorios/vendas/", RelatoriosVendasView.as_view(), name="relatorios-vendas"),
    path("relatorios/inadimplencia/", InadimplenciaView.as_view(), name="relatorios-inadimplencia"),
    path("relatorios/estoque/", RelatoriosEstoqueView.as_view(), name="relatorios-estoque"),
]
