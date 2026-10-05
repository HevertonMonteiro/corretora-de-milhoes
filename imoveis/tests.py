import io
import shutil
import tempfile

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import Imovel, ImovelFoto


class ImovelModelTests(TestCase):
    def test_codigo_referencia_e_slug_sao_gerados_automaticamente(self):
        imovel = Imovel.objects.create(
            titulo="Casa com piscina",
            tipo_negocio=Imovel.TipoNegocio.VENDA,
            tipo_imovel=Imovel.TipoImovel.CASA,
            valor="500000.00",
            cidade="Recife",
            bairro="Casa Forte",
        )
        self.assertTrue(imovel.codigo_referencia.startswith("CM-"))
        self.assertTrue(imovel.slug)

    def test_esta_disponivel_reflete_status(self):
        imovel = Imovel.objects.create(
            titulo="Terreno",
            tipo_negocio=Imovel.TipoNegocio.VENDA,
            tipo_imovel=Imovel.TipoImovel.TERRENO,
            valor="120000.00",
            cidade="Recife",
            bairro="Várzea",
            status=Imovel.Status.VENDIDO,
        )
        self.assertFalse(imovel.esta_disponivel)


class VitrineViewTests(TestCase):
    def setUp(self):
        self.disponivel = Imovel.objects.create(
            titulo="Apartamento disponível",
            tipo_negocio=Imovel.TipoNegocio.ALUGUEL,
            tipo_imovel=Imovel.TipoImovel.APARTAMENTO,
            valor="2000.00",
            cidade="Recife",
            bairro="Boa Viagem",
            status=Imovel.Status.DISPONIVEL,
        )
        Imovel.objects.create(
            titulo="Apartamento inativo",
            tipo_negocio=Imovel.TipoNegocio.ALUGUEL,
            tipo_imovel=Imovel.TipoImovel.APARTAMENTO,
            valor="2000.00",
            cidade="Recife",
            bairro="Boa Viagem",
            status=Imovel.Status.INATIVO,
        )

    def test_vitrine_lista_apenas_nao_inativos(self):
        response = self.client.get(reverse("imoveis:vitrine"))
        self.assertEqual(response.status_code, 200)
        imoveis = list(response.context["imoveis"])
        self.assertIn(self.disponivel, imoveis)
        self.assertEqual(len(imoveis), 1)

    def test_vitrine_filtra_por_tipo_negocio(self):
        response = self.client.get(reverse("imoveis:vitrine"), {"tipo_negocio": "venda"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["imoveis"]), 0)

    def test_detalhe_retorna_200_para_slug_existente(self):
        response = self.client.get(
            reverse("imoveis:detalhe", kwargs={"slug": self.disponivel.slug})
        )
        self.assertEqual(response.status_code, 200)

    def test_detalhe_retorna_404_para_slug_inexistente(self):
        response = self.client.get(
            reverse("imoveis:detalhe", kwargs={"slug": "nao-existe"})
        )
        self.assertEqual(response.status_code, 404)


def _jpeg_bytes():
    buffer = io.BytesIO()
    Image.new("RGB", (20, 20), "blue").save(buffer, format="JPEG")
    return buffer.getvalue()


class ArquivoDaFotoTests(TestCase):
    def setUp(self):
        self.media = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.media)
        self.override.enable()

    def tearDown(self):
        self.override.disable()
        shutil.rmtree(self.media, ignore_errors=True)

    def _imovel_com_foto(self):
        imovel = Imovel.objects.create(
            titulo="Casa com fotos",
            tipo_negocio=Imovel.TipoNegocio.VENDA,
            tipo_imovel=Imovel.TipoImovel.CASA,
            valor="500000.00",
            cidade="Recife",
            bairro="Casa Forte",
        )
        caminho = default_storage.save("imoveis/teste/a.jpg", ContentFile(_jpeg_bytes()))
        foto = ImovelFoto.objects.create(imovel=imovel, imagem=caminho, ordem=0)
        return imovel, foto

    def test_excluir_imovel_apaga_arquivo_da_foto(self):
        imovel, foto = self._imovel_com_foto()
        caminho = foto.imagem.name
        with self.captureOnCommitCallbacks(execute=True):
            imovel.delete()
        self.assertFalse(default_storage.exists(caminho))

    def test_trocar_foto_apaga_arquivo_antigo(self):
        imovel, foto = self._imovel_com_foto()
        antigo = foto.imagem.name
        novo = default_storage.save("imoveis/teste/b.jpg", ContentFile(_jpeg_bytes()))
        with self.captureOnCommitCallbacks(execute=True):
            foto.imagem = novo
            foto.save()
        self.assertFalse(default_storage.exists(antigo))
        self.assertTrue(default_storage.exists(novo))

