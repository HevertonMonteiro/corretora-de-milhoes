from django.db import models

from imoveis.models import Imovel


class Lead(models.Model):
    """Todo contato feito pelo formulário do site. Guardamos aqui ANTES de
    redirecionar para o WhatsApp, para a corretora ter um histórico/CRM
    simples de quem já demonstrou interesse — coisa que o link de WhatsApp
    sozinho não oferece."""

    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    mensagem = models.TextField(blank=True)
    imovel_relacionado = models.ForeignKey(
        Imovel, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="leads",
    )

    atendido = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "Contato / Lead"
        verbose_name_plural = "Contatos / Leads"

    def __str__(self):
        return f"{self.nome} · {self.criado_em:%d/%m/%Y}"

    def link_whatsapp(self):
        """Monta o link wa.me com a mensagem já preenchida, apontando para
        o número da corretora cadastrado em PerfilCorretora."""
        from urllib.parse import quote

        from perfil.models import PerfilCorretora

        perfil = PerfilCorretora.objects.first()
        numero = perfil.whatsapp if perfil else ""

        partes = [f"Olá, meu nome é {self.nome}."]
        if self.imovel_relacionado:
            partes.append(
                f"Tenho interesse no imóvel {self.imovel_relacionado.codigo_referencia} "
                f"({self.imovel_relacionado.titulo})."
            )
        if self.mensagem:
            partes.append(self.mensagem)
        texto = quote(" ".join(partes))

        return f"https://wa.me/{numero}?text={texto}"
