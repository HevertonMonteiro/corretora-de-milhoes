from django.contrib import admin

from .models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("nome", "telefone", "imovel_relacionado", "atendido", "criado_em")
    list_filter = ("atendido",)
    list_editable = ("atendido",)
    search_fields = ("nome", "telefone", "email")
