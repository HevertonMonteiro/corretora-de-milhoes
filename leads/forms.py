from django import forms

from .models import Lead


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ["nome", "telefone", "email", "mensagem", "imovel_relacionado"]
        widgets = {
            "imovel_relacionado": forms.HiddenInput(),
            "mensagem": forms.Textarea(attrs={"rows": 4}),
        }
