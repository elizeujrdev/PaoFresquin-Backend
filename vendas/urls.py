from rest_framework.routers import DefaultRouter

from vendas.views import VendaViewSet

router = DefaultRouter()
router.register("", VendaViewSet, basename="venda")

urlpatterns = router.urls
