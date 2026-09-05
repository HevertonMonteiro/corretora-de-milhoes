import re

from django.db import models
from django.core.exceptions import ValidationError

from core.imagens import redimensionar_imagem


class PerfilCorretora(models.Model):
    """Dados públicos da corretora — CRECI, região de atuação, contatos e
    localização do escritório. Projetado como singleton: só deve existir
    UM registro (o admin usa essa regra para impedir um segundo)."""

    nome = models.CharField(max_length=120)
    foto = models.ImageField(upload_to="perfil/", blank=True, null=True)
    creci = models.CharField(
        max_length=20,
        help_text='Apenas o número do registro, ex: PE 12345 (o site já mostra o rótulo "CRECI -" na frente).',
    )
    bio = models.TextField(blank=True)
    regiao_atuacao = models.CharField(
        max_length=200, help_text="Ex: Recife, Boa Viagem, Casa Forte e região"
    )

    # Contato
    whatsapp = models.CharField(
        max_length=20,
        help_text="Formato internacional, ex: 5581999999999 (funciona mesmo se "
        "digitar com espaço, + ou traço — só os números é que contam).",
    )
    email = models.EmailField(blank=True)
    instagram_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)

    # Localização do escritório (para o mapa)
    endereco_escritorio = models.CharField(max_length=200, blank=True)
    latitude = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True
    )

    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil da corretora"
        verbose_name_plural = "Perfil da corretora"

    def __str__(self):
        return self.nome

    def clean(self):
        if not self.pk and PerfilCorretora.objects.exists():
            raise ValidationError(
                "Já existe um perfil cadastrado. Edite o perfil existente "
                "em vez de criar um novo."
            )

    def save(self, *args, **kwargs):
        if self.foto and not self.foto._committed:
            self.foto = redimensionar_imagem(self.foto)
        super().save(*args, **kwargs)

    @property
    def whatsapp_numero_limpo(self):
        """Só os dígitos do WhatsApp. O link do wa.me quebra se sobrar
        espaço, "+", parêntese ou traço no meio (ex: corretora digitando
        "+55 81 99999-9999" em vez de "5581999999999") — normaliza sozinho
        a cada acesso, então não depende de reeditar o cadastro."""
        return re.sub(r"\D", "", self.whatsapp or "")

    @property
    def whatsapp_link(self):
        return f"https://wa.me/{self.whatsapp_numero_limpo}"
