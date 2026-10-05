import io
import os
import shutil
import tempfile
import time
from io import StringIO

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management import call_command
from django.test import TestCase, override_settings
from PIL import Image

from imoveis.models import Imovel, ImovelFoto


def _jpeg_bytes():
    buffer = io.BytesIO()
    Image.new("RGB", (20, 20), "green").save(buffer, format="JPEG")
    return buffer.getvalue()


class LimparFotosOrfasTests(TestCase):
    def setUp(self):
        self.media = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.media)
        self.override.enable()
        imovel = Imovel.objects.create(
            titulo="Com foto",
            tipo_negocio=Imovel.TipoNegocio.VENDA,
            tipo_imovel=Imovel.TipoImovel.CASA,
            valor="500000.00",
            cidade="Recife",
            bairro="Casa Forte",
        )
        self.em_uso = default_storage.save("imoveis/2026/10/em_uso.jpg", ContentFile(_jpeg_bytes()))
        ImovelFoto.objects.create(imovel=imovel, imagem=self.em_uso, ordem=0)
        self.orfao_antigo = default_storage.save("imoveis/2026/10/orfao_antigo.jpg", ContentFile(_jpeg_bytes()))
        self.orfao_recente = default_storage.save("imoveis/2026/10/orfao_recente.jpg", ContentFile(_jpeg_bytes()))
        antigo = time.time() - 3 * 24 * 3600
        os.utime(default_storage.path(self.orfao_antigo), (antigo, antigo))

    def tearDown(self):
        self.override.disable()
        shutil.rmtree(self.media, ignore_errors=True)

    def test_sem_apagar_apenas_lista(self):
        saida = StringIO()
        call_command("limpar_fotos_orfas", stdout=saida)
        self.assertIn(self.orfao_antigo, saida.getvalue())
        self.assertNotIn(self.em_uso, saida.getvalue())
        self.assertNotIn(self.orfao_recente, saida.getvalue())
        self.assertTrue(default_storage.exists(self.orfao_antigo))

    def test_apagar_remove_so_orfaos_antigos(self):
        call_command("limpar_fotos_orfas", "--apagar", stdout=StringIO())
        self.assertFalse(default_storage.exists(self.orfao_antigo))
        self.assertTrue(default_storage.exists(self.em_uso))
        self.assertTrue(default_storage.exists(self.orfao_recente))
