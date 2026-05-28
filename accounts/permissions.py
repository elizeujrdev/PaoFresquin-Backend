from rest_framework.permissions import BasePermission

from accounts.models import Perfil


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.perfil == Perfil.ADMIN


class PodeVendas(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.pode_vendas()


class PodeCancelarVenda(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.pode_cancelar_venda()


class PodeRelatorios(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.pode_relatorios()


class PodeFuncionarios(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.pode_gerenciar_funcionarios()
