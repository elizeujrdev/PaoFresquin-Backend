from rest_framework.routers import DefaultRouter

from funcionarios.views import FuncionarioViewSet

router = DefaultRouter()
router.register("", FuncionarioViewSet, basename="funcionario")

urlpatterns = router.urls
