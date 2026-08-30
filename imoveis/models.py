import re

from django.db import models
from django.urls import reverse

# Casa qualquer formato de link do YouTube (assistir, compartilhado
# youtu.be, shorts ou já incorporado) e extrai o ID do vídeo.
YOUTUBE_ID_RE = re.compile(
    r"(?:youtube\.com/(?:watch\?v=|embed/|shorts/)|youtu\.be/)([\w-]{11})"
)


class Imovel(models.Model):
    """Um imóvel cadastrado pela corretora — o coração da vitrine pública
    e do painel de autoatendimento."""

    class TipoNegocio(models.TextChoices):
        VENDA = "venda", "Venda"
        ALUGUEL = "aluguel", "Aluguel"
        VENDA_ALUGUEL = "venda_aluguel", "Venda ou Aluguel"

    class TipoImovel(models.TextChoices):
        APARTAMENTO = "apartamento", "Apartamento"
        CASA = "casa", "Casa"
        CASA_CONDOMINIO = "casa_condominio", "Casa em Condomínio"
        TERRENO = "terreno", "Terreno / Lote"
        COMERCIAL = "comercial", "Sala / Ponto Comercial"
        RURAL = "rural", "Chácara / Sítio / Fazenda"
        COBERTURA = "cobertura", "Cobertura"
        OUTRO = "outro", "Outro"

    class Status(models.TextChoices):
        DISPONIVEL = "disponivel", "Disponível"
        RESERVADO = "reservado", "Reservado"
        VENDIDO = "vendido", "Vendido"
        ALUGADO = "alugado", "Alugado"
        INATIVO = "inativo", "Inativo (rascunho)"

    # Identificação
    titulo = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    codigo_referencia = models.CharField(
        max_length=20, unique=True, blank=True,
        help_text="Gerado automaticamente (ex: CM-0001) se deixado em branco.",
    )
    descricao = models.TextField(blank=True)

    # Classificação
    tipo_negocio = models.CharField(max_length=20, choices=TipoNegocio.choices)
    tipo_imovel = models.CharField(max_length=20, choices=TipoImovel.choices)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DISPONIVEL
    )

    # Valores
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    valor_condominio = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    valor_iptu = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    # Características físicas
    area_construida = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True, help_text="m²"
    )
    area_terreno = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True, help_text="m²"
    )
    quartos = models.PositiveSmallIntegerField(default=0)
    suites = models.PositiveSmallIntegerField(default=0)
    banheiros = models.PositiveSmallIntegerField(default=0)
    vagas_garagem = models.PositiveSmallIntegerField(default=0)

    # Localização
    cidade = models.CharField(max_length=80)
    bairro = models.CharField(max_length=80)
    endereco = models.CharField(max_length=200, blank=True)
    cep = models.CharField(max_length=9, blank=True)
    latitude = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True
    )

    # Destaque / marketing
    destaque = models.BooleanField(
        default=False, help_text="Aparece em posição de destaque na vitrine."
    )
    video_url = models.URLField(blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-destaque", "-criado_em"]
        verbose_name = "Imóvel"
        verbose_name_plural = "Imóveis"

    def __str__(self):
        return f"{self.codigo_referencia} · {self.titulo}"

    def save(self, *args, **kwargs):
        if not self.codigo_referencia:
            ultimo = Imovel.objects.order_by("id").last()
            proximo_id = (ultimo.id + 1) if ultimo else 1
            self.codigo_referencia = f"CM-{proximo_id:04d}"
        if not self.slug:
            from django.utils.text import slugify

            base_slug = slugify(f"{self.titulo}-{self.codigo_referencia}")
            self.slug = base_slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("imoveis:detalhe", kwargs={"slug": self.slug})

    @property
    def esta_disponivel(self):
        return self.status == self.Status.DISPONIVEL

    @property
    def video_embed_url(self):
        """Sempre serve o vídeo pelo domínio youtube-nocookie.com — evita o
        "Erro 153" que o player do YouTube mostra em navegadores com
        bloqueio de rastreamento entre sites ligado (ex: Safari com
        "Impedir Rastreamento entre Sites"), que quebra o embed no domínio
        normal youtube.com. Reprocessa o link salvo a cada acesso, então
        corrige sozinho até imóveis salvos antes desse ajuste."""
        if not self.video_url:
            return ""
        match = YOUTUBE_ID_RE.search(self.video_url)
        if match:
            return f"https://www.youtube-nocookie.com/embed/{match.group(1)}"
        return self.video_url


class ImovelFoto(models.Model):
    """Fotos do imóvel. A primeira (menor `ordem`) é usada como capa."""

    imovel = models.ForeignKey(
        Imovel, related_name="fotos", on_delete=models.CASCADE
    )
    imagem = models.ImageField(upload_to="imoveis/%Y/%m/")
    titulo = models.CharField(
        "título", max_length=120, blank=True,
        help_text="Nome do cômodo mostrado embaixo da foto, ex: Sala, Quarto 1, Varanda.",
    )
    ordem = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["ordem", "id"]
        verbose_name = "Foto do imóvel"
        verbose_name_plural = "Fotos do imóvel"

    def __str__(self):
        return f"Foto de {self.imovel.titulo} ({self.ordem})"


class Realizacao(models.Model):
    """Post de 'negócio fechado' que a corretora publica no próprio site —
    a versão sob controle dela do que hoje ela posta no Instagram."""

    imovel = models.ForeignKey(
        Imovel, related_name="realizacoes", on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    titulo = models.CharField(
        max_length=120, help_text="Ex: 'Mais uma chave entregue no Boa Viagem!'"
    )
    texto = models.TextField(blank=True)
    foto = models.ImageField(upload_to="realizacoes/%Y/%m/")
    publicado_em = models.DateTimeField(auto_now_add=True)
    visivel = models.BooleanField(default=True)

    class Meta:
        ordering = ["-publicado_em"]
        verbose_name = "Realização (negócio fechado)"
        verbose_name_plural = "Realizações (negócios fechados)"

    def __str__(self):
        return self.titulo
