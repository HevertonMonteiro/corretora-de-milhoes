from django.contrib import admin

from .models import Depoimento


@admin.register(Depoimento)
class DepoimentoAdmin(admin.ModelAdmin):
    list_display = ("nome_cliente", "nota", "aprovado", "criado_em")
    list_filter = ("aprovado", "nota")
    list_editable = ("aprovado",)
    search_fields = ("nome_cliente", "texto")
