from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from imoveis.models import Imovel


class Depoimento(models.Model):
    """Feedback de um cliente externo. Enviado pelo formulário público,
    fica invisível na vitrine até a corretora aprovar no painel — evita
    spam e reviews falsos."""

    nome_cliente = models.CharField(max_length=100)
    email_cliente = models.EmailField(
        blank=True, help_text="Não é exibido publicamente."
    )
    texto = models.TextField()
    nota = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="De 1 a 5 estrelas.",
    )
    imovel_relacionado = models.ForeignKey(
        Imovel, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="depoimentos",
    )

    aprovado = models.BooleanField(
        default=False, help_text="Só aparece no site depois de aprovado."
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "Depoimento"
        verbose_name_plural = "Depoimentos"

    def __str__(self):
        status = "aprovado" if self.aprovado else "pendente"
        return f"{self.nome_cliente} ({self.nota}★, {status})"

    @property
    def estrelas(self):
        return "★" * self.nota
