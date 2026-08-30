from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse

from core.ratelimit import limitar_por_ip

from .forms import DepoimentoForm


@limitar_por_ip("depoimentos_novo", max_tentativas=5, janela_segundos=600)
def novo(request):
    """Formulário público para o cliente deixar feedback. Fica pendente
    de aprovação da corretora antes de aparecer no site (ver painel)."""
    if request.method == "POST":
        form = DepoimentoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Obrigado pelo seu depoimento! Ele será publicado após "
                "revisão.",
            )
            return redirect(reverse("home"))
    else:
        form = DepoimentoForm()
    return render(request, "depoimentos/novo.html", {"form": form})
