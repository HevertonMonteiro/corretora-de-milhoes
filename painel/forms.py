from django import forms
from django.forms import inlineformset_factory

from imoveis.models import YOUTUBE_ID_RE, Imovel, ImovelFoto, Realizacao
from perfil.models import PerfilCorretora


MAX_FOTOS_POR_IMOVEL = 9


class ImovelForm(forms.ModelForm):
    class Meta:
        model = Imovel
        # latitude/longitude ficam de fora — não tem mapa do imóvel no site.
        exclude = [
            "slug", "codigo_referencia", "criado_em", "atualizado_em",
            "latitude", "longitude",
        ]
        widgets = {
            "descricao": forms.Textarea(attrs={"rows": 5}),
        }
        help_texts = {
            "video_url": (
                "Cole o link do vídeo do YouTube — funciona com o link normal, "
                "o de compartilhar (youtu.be) ou o de incorporação. "
                "Até 1 vídeo por imóvel."
            ),
        }

    def clean_video_url(self):
        """A corretora costuma colar o link que o YouTube dá ao clicar em
        "Compartilhar" (ex: youtu.be/ID), que o navegador recusa a exibir
        dentro do iframe da página do imóvel. Convertemos automaticamente
        para o formato de incorporação (/embed/ID), que é o único que
        funciona dentro de um iframe."""
        url = self.cleaned_data.get("video_url", "")
        if url:
            match = YOUTUBE_ID_RE.search(url)
            if match:
                return f"https://www.youtube.com/embed/{match.group(1)}"
        return url


# Formset para a corretora subir várias fotos do imóvel de uma vez só.
# max_num/validate_max travam o limite em 9 fotos por imóvel.
ImovelFotoFormSet = inlineformset_factory(
    Imovel,
    ImovelFoto,
    fields=["imagem", "titulo", "ordem"],
    extra=MAX_FOTOS_POR_IMOVEL,
    max_num=MAX_FOTOS_POR_IMOVEL,
    validate_max=True,
    can_delete=True,
)


class RealizacaoForm(forms.ModelForm):
    class Meta:
        model = Realizacao
        fields = ["imovel", "titulo", "texto", "foto", "visivel"]
        widgets = {
            "texto": forms.Textarea(attrs={"rows": 4}),
        }


class PerfilForm(forms.ModelForm):
    class Meta:
        model = PerfilCorretora
        # facebook_url fica de fora — a corretora não usa Facebook no site.
        # latitude/longitude também ficam de fora — não tem nenhum mapa do
        # escritório no site (só o mapa de cada imóvel, que é outro campo).
        exclude = ["facebook_url", "latitude", "longitude", "atualizado_em"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 5}),
        }
        help_texts = {
            "whatsapp": "Formato internacional, sem espaços ou símbolos. Ex: 5581999999999",
        }
