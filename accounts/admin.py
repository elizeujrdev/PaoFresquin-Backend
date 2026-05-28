from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from accounts.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "perfil", "loja", "ativo", "is_staff")
    list_filter = ("perfil", "ativo")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Pão FresQUIM", {"fields": ("perfil", "loja", "ativo")}),
    )
