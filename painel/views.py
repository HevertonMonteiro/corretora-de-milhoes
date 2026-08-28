from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy

from imoveis.models import Imovel, Realizacao
from depoimentos.models import Depoimento
from leads.models import Lead
from perfil.models import PerfilCorretora

from .forms import ImovelForm, ImovelFotoFormSet, RealizacaoForm, PerfilForm


class PainelLoginView(LoginView):
    template_name = "painel/login.html"


class PainelLogoutView(LogoutView):
    next_page = "painel:login"


@login_required
def dashboard(request):
    context = {
        "total_imoveis": Imovel.objects.count(),
        "total_disponiveis": Imovel.objects.filter(
            status=Imovel.Status.DISPONIVEL
        ).count(),
        "total_fechados": Imovel.objects.filter(
            status__in=[Imovel.Status.VENDIDO, Imovel.Status.ALUGADO]
        ).count(),
        "leads_pendentes": Lead.objects.filter(atendido=False).count(),
        "depoimentos_pendentes": Depoimento.objects.filter(aprovado=False).count(),
    }
    return render(request, "painel/dashboard.html", context)


@login_required
def imovel_list(request):
    imoveis = Imovel.objects.all()
    return render(request, "painel/imovel_list.html", {"imoveis": imoveis})


@login_required
def imovel_form(request, pk=None):
    """Uma view só para criar E editar — evita duplicar o formulário e o
    tratamento do formset de fotos."""
    imovel = get_object_or_404(Imovel, pk=pk) if pk else None

    if request.method == "POST":
        form = ImovelForm(request.POST, instance=imovel)
        fotos_formset = ImovelFotoFormSet(
            request.POST, request.FILES, instance=imovel or Imovel()
        )
        if form.is_valid():
            imovel = form.save()
            fotos_formset = ImovelFotoFormSet(
                request.POST, request.FILES, instance=imovel
            )
            if fotos_formset.is_valid():
                fotos_formset.save()
            messages.success(request, "Imóvel salvo com sucesso.")
            return redirect(reverse("painel:imovel_list"))
    else:
        form = ImovelForm(instance=imovel)
        fotos_formset = ImovelFotoFormSet(instance=imovel)

    return render(
        request,
        "painel/imovel_form.html",
        {"form": form, "fotos_formset": fotos_formset, "imovel": imovel},
    )


@login_required
def imovel_delete(request, pk):
    imovel = get_object_or_404(Imovel, pk=pk)
    if request.method == "POST":
        imovel.delete()
        messages.success(request, "Imóvel removido.")
        return redirect(reverse("painel:imovel_list"))
    return render(request, "painel/imovel_confirm_delete.html", {"imovel": imovel})


@login_required
def imovel_status(request, pk):
    """Ação rápida: marcar como vendido/alugado/disponível direto da
    listagem, sem precisar abrir o formulário completo."""
    imovel = get_object_or_404(Imovel, pk=pk)
    novo_status = request.POST.get("status")
    if request.method == "POST" and novo_status in Imovel.Status.values:
        imovel.status = novo_status
        imovel.save(update_fields=["status", "atualizado_em"])
        messages.success(request, f"Status atualizado para {imovel.get_status_display()}.")
    return redirect(reverse("painel:imovel_list"))


@login_required
def realizacao_create(request):
    if request.method == "POST":
        form = RealizacaoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Publicação de negócio fechado criada.")
            return redirect(reverse("painel:dashboard"))
    else:
        form = RealizacaoForm()
    return render(request, "painel/realizacao_form.html", {"form": form})


@login_required
def depoimentos_moderar(request):
    if request.method == "POST":
        depoimento = get_object_or_404(Depoimento, pk=request.POST.get("id"))
        acao = request.POST.get("acao")
        if acao == "aprovar":
            depoimento.aprovado = True
            depoimento.save(update_fields=["aprovado"])
        elif acao == "excluir":
            depoimento.delete()
        return redirect(reverse("painel:depoimentos_moderar"))

    depoimentos = Depoimento.objects.all()
    return render(request, "painel/depoimentos_list.html", {"depoimentos": depoimentos})


@login_required
def leads_list(request):
    if request.method == "POST":
        lead = get_object_or_404(Lead, pk=request.POST.get("id"))
        lead.atendido = not lead.atendido
        lead.save(update_fields=["atendido"])
        return redirect(reverse("painel:leads_list"))

    leads = Lead.objects.all()
    return render(request, "painel/leads_list.html", {"leads": leads})


@login_required
def perfil_editar(request):
    """Perfil é um singleton: sempre edita o único registro existente, ou
    cria o primeiro se ainda não houver nenhum (ex: banco novo em produção)."""
    perfil = PerfilCorretora.objects.first()

    if request.method == "POST":
        form = PerfilForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil atualizado com sucesso.")
            return redirect(reverse("painel:perfil_editar"))
    else:
        form = PerfilForm(instance=perfil)

    return render(request, "painel/perfil_form.html", {"form": form, "perfil_existe": perfil is not None})
