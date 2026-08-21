from django import forms

from .models import Depoimento


class DepoimentoForm(forms.ModelForm):
    class Meta:
        model = Depoimento
        fields = ["nome_cliente", "email_cliente", "nota", "texto", "imovel_relacionado"]
        widgets = {
            "texto": forms.Textarea(attrs={"rows": 4}),
            "nota": forms.Select(choices=[(i, f"{i} estrela(s)") for i in range(1, 6)]),
        }
