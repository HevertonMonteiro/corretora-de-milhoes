from django import forms
from django.forms import inlineformset_factory

from imoveis.models import Imovel, ImovelFoto, Realizacao


MAX_FOTOS_POR_IMOVEL = 9


class ImovelForm(forms.ModelForm):
    class Meta:
        model = Imovel
        exclude = ["slug", "codigo_referencia", "criado_em", "atualizado_em"]
        widgets = {
            "descricao": forms.Textarea(attrs={"rows": 5}),
        }
        help_texts = {
            "video_url": (
                "Link de incorporação do YouTube (ex: https://www.youtube.com/embed/ID) "
                "— até 1 vídeo por imóvel."
            ),
        }


# Formset para a corretora subir várias fotos do imóvel de uma vez só.
# max_num/validate_max travam o limite em 9 fotos por imóvel.
ImovelFotoFormSet = inlineformset_factory(
    Imovel,
    ImovelFoto,
    fields=["imagem", "legenda", "ordem"],
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
