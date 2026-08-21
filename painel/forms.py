from django import forms
from django.forms import inlineformset_factory

from imoveis.models import Imovel, ImovelFoto, Realizacao


class ImovelForm(forms.ModelForm):
    class Meta:
        model = Imovel
        exclude = ["slug", "codigo_referencia", "criado_em", "atualizado_em"]
        widgets = {
            "descricao": forms.Textarea(attrs={"rows": 5}),
        }


# Formset para a corretora subir várias fotos do imóvel de uma vez só.
ImovelFotoFormSet = inlineformset_factory(
    Imovel,
    ImovelFoto,
    fields=["imagem", "legenda", "ordem"],
    extra=3,
    can_delete=True,
)


class RealizacaoForm(forms.ModelForm):
    class Meta:
        model = Realizacao
        fields = ["imovel", "titulo", "texto", "foto", "visivel"]
        widgets = {
            "texto": forms.Textarea(attrs={"rows": 4}),
        }
