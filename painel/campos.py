import re

from django import forms
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

PASTAS_PERMITIDAS = ("imoveis", "realizacoes", "perfil")

_CAMINHO_RE = re.compile(
    r"^(?:imoveis|realizacoes|perfil)/[A-Za-z0-9_\-/]+\.[A-Za-z0-9]{2,5}$"
)


def validar_caminho_imagem(valor):
    if ".." in valor or not _CAMINHO_RE.match(valor):
        raise ValidationError("Caminho de foto inválido.")


class CaminhoImagemWidget(forms.Widget):
    """Input de foto que sobe a imagem sozinha assim que é escolhida.

    O navegador reduz a foto e envia para o endpoint de upload; o caminho
    devolvido vai para um campo oculto, que é o único valor enviado com o
    formulário. O input de arquivo fica sem `name`, então o arquivo original
    nunca entra na requisição do formulário (o que estouraria o limite de
    tamanho das funções serverless)."""

    def __init__(self, pasta, attrs=None):
        self.pasta = pasta
        super().__init__(attrs)

    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        campo_id = attrs.get("id", "")
        oculto = forms.HiddenInput().render(
            name, value, {"data-caminho-imagem": ""}, renderer
        )
        arquivo = format_html(
            '<input type="file" accept="image/*" id="{}" data-upload-foto '
            'data-upload-url="{}" data-pasta="{}">',
            campo_id,
            reverse("painel:upload_imagem"),
            self.pasta,
        )
        status = format_html('<span class="upload-status" data-upload-status></span>')
        return mark_safe(f"{oculto}{arquivo}{status}")


class CaminhoImagemField(forms.CharField):
    def __init__(self, pasta, **kwargs):
        kwargs.setdefault("max_length", 255)
        kwargs.setdefault("widget", CaminhoImagemWidget(pasta))
        super().__init__(**kwargs)
        self.validators.append(validar_caminho_imagem)
