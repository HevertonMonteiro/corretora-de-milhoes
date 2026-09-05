from django.shortcuts import render

from imoveis.models import Imovel, Realizacao
from depoimentos.models import Depoimento


def home(request):
    context = {
        "imoveis_destaque": Imovel.objects.filter(
            destaque=True, status=Imovel.Status.DISPONIVEL
        ).prefetch_related("fotos")[:6],
        "realizacoes": Realizacao.objects.filter(visivel=True)[:6],
        "depoimentos": Depoimento.objects.filter(aprovado=True)[:6],
        "total_fechados": Imovel.objects.filter(
            status__in=[Imovel.Status.VENDIDO, Imovel.Status.ALUGADO]
        ).count(),
        "total_disponiveis": Imovel.objects.filter(
            status=Imovel.Status.DISPONIVEL
        ).count(),
        "total_depoimentos": Depoimento.objects.filter(aprovado=True).count(),
        "total_cidades": Imovel.objects.exclude(status=Imovel.Status.INATIVO)
        .values("cidade").distinct().count(),
    }
    return render(request, "core/home.html", context)
