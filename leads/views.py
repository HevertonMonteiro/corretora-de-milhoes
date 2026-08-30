from django.shortcuts import render, redirect

from core.ratelimit import limitar_por_ip

from .forms import LeadForm


@limitar_por_ip("leads_contato", max_tentativas=5, janela_segundos=600)
def contato(request):
    """Formulário de contato. Salva o lead no banco (histórico/CRM da
    corretora) e redireciona para o WhatsApp com a mensagem pré-preenchida
    — o melhor dos dois mundos: ela não perde nenhum contato e ainda
    responde pelo canal que já usa no dia a dia."""
    whatsapp_link = None
    if request.method == "POST":
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save()
            whatsapp_link = lead.link_whatsapp()
            return redirect(whatsapp_link)
    else:
        form = LeadForm(initial={
            "imovel_relacionado": request.GET.get("imovel"),
        })
    return render(request, "leads/contato.html", {"form": form})
