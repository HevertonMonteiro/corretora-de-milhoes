from django.shortcuts import render, get_object_or_404

from .models import Imovel


def vitrine(request):
    """Vitrine pública com busca e filtros — a página mais importante do
    site do ponto de vista de quem está procurando imóvel."""
    imoveis = Imovel.objects.exclude(status=Imovel.Status.INATIVO).prefetch_related("fotos")

    tipo_negocio = request.GET.get("tipo_negocio")
    tipo_imovel = request.GET.get("tipo_imovel")
    cidade = request.GET.get("cidade")
    bairro = request.GET.get("bairro")
    quartos_min = request.GET.get("quartos_min")
    valor_min = request.GET.get("valor_min")
    valor_max = request.GET.get("valor_max")
    busca = request.GET.get("q")

    if tipo_negocio:
        imoveis = imoveis.filter(tipo_negocio=tipo_negocio)
    if tipo_imovel:
        imoveis = imoveis.filter(tipo_imovel=tipo_imovel)
    if cidade:
        imoveis = imoveis.filter(cidade__icontains=cidade)
    if bairro:
        imoveis = imoveis.filter(bairro__icontains=bairro)
    if quartos_min:
        imoveis = imoveis.filter(quartos__gte=quartos_min)
    if valor_min:
        imoveis = imoveis.filter(valor__gte=valor_min)
    if valor_max:
        imoveis = imoveis.filter(valor__lte=valor_max)
    if busca:
        imoveis = imoveis.filter(titulo__icontains=busca)

    context = {
        "imoveis": imoveis,
        "tipos_negocio": Imovel.TipoNegocio.choices,
        "tipos_imovel": Imovel.TipoImovel.choices,
        "filtros": request.GET,
    }
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return render(request, "imoveis/_grid.html", context)
    return render(request, "imoveis/vitrine.html", context)


def detalhe(request, slug):
    imovel = get_object_or_404(
        Imovel.objects.exclude(status=Imovel.Status.INATIVO), slug=slug
    )
    context = {"imovel": imovel}
    return render(request, "imoveis/detalhe.html", context)
