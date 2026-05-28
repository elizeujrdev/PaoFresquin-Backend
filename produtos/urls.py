from rest_framework.routers import DefaultRouter

from produtos.views import CategoriaViewSet, ProdutoViewSet

router = DefaultRouter()
router.register("categorias", CategoriaViewSet, basename="categoria")
router.register("", ProdutoViewSet, basename="produto")

urlpatterns = router.urls
