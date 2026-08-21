from django.shortcuts import render

from imoveis.models import Imovel, Realizacao
from depoimentos.models import Depoimento


def home(request):
    context = {
        "imoveis_destaque": Imovel.objects.filter(
            destaque=True, status=Imovel.Status.DISPONIVEL
        )[:6],
        "realizacoes": Realizacao.objects.filter(visivel=True)[:6],
        "depoimentos": Depoimento.objects.filter(aprovado=True)[:6],
    }
    return render(request, "core/home.html", context)
