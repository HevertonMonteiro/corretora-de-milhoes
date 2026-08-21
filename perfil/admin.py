from django.contrib import admin

from .models import PerfilCorretora


@admin.register(PerfilCorretora)
class PerfilCorretoraAdmin(admin.ModelAdmin):
    list_display = ("nome", "creci", "whatsapp", "regiao_atuacao")

    def has_add_permission(self, request):
        # Singleton: só permite adicionar se ainda não existir nenhum.
        return not PerfilCorretora.objects.exists()
