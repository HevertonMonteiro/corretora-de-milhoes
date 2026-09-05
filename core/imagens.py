import io

from django.core.files.base import ContentFile
from PIL import Image, ImageOps

# Fotos de celular costumam vir enormes (vários MB, resolução de câmera
# inteira) mesmo pra aparecer num cartão pequeno no site — isso é a maior
# causa de carregamento lento no site. Redimensionamos e recomprimimos
# toda foto enviada antes de guardar, sem perda perceptível de qualidade.
MAX_DIMENSAO = 1920
QUALIDADE_JPEG = 82


def redimensionar_imagem(arquivo, max_dimensao=MAX_DIMENSAO, qualidade=QUALIDADE_JPEG):
    """Recebe o arquivo de imagem enviado no formulário e devolve uma
    versão redimensionada (no máximo `max_dimensao` px no lado maior) e
    recomprimida como JPEG, pronta pra substituir o arquivo original antes
    de salvar."""
    imagem = Image.open(arquivo)
    # Pede pro decodificador JPEG já entregar a imagem numa escala menor,
    # em vez de descomprimir o arquivo inteiro na resolução original só
    # pra depois reduzir — uma foto de celular moderna (48MP+) pode exigir
    # bem mais de 100MB de memória só nesse passo, o que derruba o
    # servidor no plano gratuito do Render (pouca RAM disponível). Não
    # tem efeito em formatos que não sejam JPEG (é ignorado nesse caso).
    imagem.draft("RGB", (max_dimensao, max_dimensao))
    # Corrige fotos de celular que vêm giradas (a câmera grava a rotação
    # real só nos metadados EXIF, não no pixel em si).
    imagem = ImageOps.exif_transpose(imagem)
    if imagem.mode not in ("RGB", "L"):
        imagem = imagem.convert("RGB")

    if imagem.width > max_dimensao or imagem.height > max_dimensao:
        imagem.thumbnail((max_dimensao, max_dimensao), Image.LANCZOS)

    buffer = io.BytesIO()
    imagem.save(buffer, format="JPEG", quality=qualidade, optimize=True)
    buffer.seek(0)

    nome_original = arquivo.name.rsplit(".", 1)[0]
    return ContentFile(buffer.read(), name=f"{nome_original}.jpg")
