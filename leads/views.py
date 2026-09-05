import logging

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render

from core.ratelimit import limitar_por_ip
from perfil.models import PerfilCorretora

from .forms import LeadForm

logger = logging.getLogger(__name__)


def _enviar_email_notificacao(request, lead):
    """Avisa a corretora por e-mail sobre o novo contato. Envolvido num
    try/except amplo de propósito — se o e-mail falhar por qualquer
    motivo (SMTP mal configurado, fora do ar, etc.), o cliente não pode
    ficar sem resposta só por causa disso; o lead já está salvo no painel
    de qualquer jeito. O fail_silently do Django cobre a maioria dos
    erros de SMTP, mas o try/except aqui garante que NADA relacionado a
    e-mail derruba o formulário do cliente."""
    try:
        perfil = PerfilCorretora.objects.first()
        destinatario = perfil.email if perfil else ""
        if not destinatario:
            return

        linhas = [f"Nome: {lead.nome}", f"Telefone: {lead.telefone}"]
        if lead.email:
            linhas.append(f"E-mail: {lead.email}")
        if lead.imovel_relacionado:
            link_imovel = request.build_absolute_uri(
                lead.imovel_relacionado.get_absolute_url()
            )
            linhas.append(
                f"Imóvel: {lead.imovel_relacionado.codigo_referencia} - "
                f"{lead.imovel_relacionado.titulo}\n{link_imovel}"
            )
        if lead.mensagem:
            linhas.append(f"Mensagem: {lead.mensagem}")

        send_mail(
            subject=f"Novo contato pelo site — {lead.nome}",
            message="\n".join(linhas),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[destinatario],
            fail_silently=True,
        )
    except Exception:
        logger.exception("Falha ao enviar e-mail de notificação de lead")


@limitar_por_ip("leads_contato", max_tentativas=5, janela_segundos=600)
def contato(request):
    """Formulário de contato. Salva o lead no banco (histórico/CRM da
    corretora), avisa ela por e-mail e pergunta pro cliente se quer
    continuar a conversa no WhatsApp (com a mensagem já pronta) — assim
    a corretora não perde nenhum contato e o cliente ainda tem a opção
    rápida de falar por WhatsApp na hora."""
    if request.method == "POST":
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save()
            _enviar_email_notificacao(request, lead)
            return render(request, "leads/sucesso.html", {
                "whatsapp_link": lead.link_whatsapp(),
            })
    else:
        form = LeadForm(initial={
            "imovel_relacionado": request.GET.get("imovel"),
        })
    return render(request, "leads/contato.html", {"form": form})
