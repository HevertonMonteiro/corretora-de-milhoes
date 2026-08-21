from django.contrib import admin

from .models import Imovel, ImovelFoto, Realizacao


class ImovelFotoInline(admin.TabularInline):
    model = ImovelFoto
    extra = 1


@admin.register(Imovel)
class ImovelAdmin(admin.ModelAdmin):
    list_display = (
        "codigo_referencia", "titulo", "tipo_negocio", "tipo_imovel",
        "bairro", "cidade", "valor", "status", "destaque",
    )
    list_filter = ("status", "tipo_negocio", "tipo_imovel", "cidade", "bairro")
    search_fields = ("titulo", "codigo_referencia", "bairro", "cidade")
    prepopulated_fields = {"slug": ("titulo",)}
    inlines = [ImovelFotoInline]
    list_editable = ("status", "destaque")


@admin.register(Realizacao)
class RealizacaoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "imovel", "publicado_em", "visivel")
    list_filter = ("visivel",)
