import io
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from painel.campos import validar_caminho_imagem
from painel.forms import RealizacaoForm


class PainelAcessoTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="corretora", password="senha-super-segura-123"
        )

    def test_dashboard_redireciona_anonimo_para_login(self):
        response = self.client.get(reverse("painel:dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("painel:login"), response.url)

    def test_dashboard_acessivel_apos_login(self):
        self.client.login(username="corretora", password="senha-super-segura-123")
        response = self.client.get(reverse("painel:dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_imovel_list_acessivel_apos_login(self):
        self.client.login(username="corretora", password="senha-super-segura-123")
        response = self.client.get(reverse("painel:imovel_list"))
        self.assertEqual(response.status_code, 200)


import io
import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage
from django.test import override_settings
from PIL import Image

from painel.campos import validar_caminho_imagem
from painel.forms import RealizacaoForm
from django.core.exceptions import ValidationError

def _imagem_jpeg(largura, altura):
    buffer = io.BytesIO()
    Image.new("RGB", (largura, altura), "red").save(buffer, format="JPEG")
    return buffer.getvalue()


class UploadImagemTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="corretora", password="senha-super-segura-123"
        )
        self.client.login(username="corretora", password="senha-super-segura-123")
        self.media = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.media)
        self.override.enable()
        self.url = reverse("painel:upload_imagem")

    def tearDown(self):
        self.override.disable()
        shutil.rmtree(self.media, ignore_errors=True)

    def _enviar(self, pasta="imoveis", conteudo=None, nome="foto.jpg"):
        arquivo = SimpleUploadedFile(nome, conteudo or _imagem_jpeg(10, 10), content_type="image/jpeg")
        return self.client.post(self.url, {"pasta": pasta, "arquivo": arquivo})

    def test_exige_login(self):
        self.client.logout()
        response = self._enviar()
        self.assertEqual(response.status_code, 302)

    def test_aceita_apenas_post(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_rejeita_pasta_fora_da_lista(self):
        self.assertEqual(self._enviar(pasta="../etc").status_code, 400)

    def test_rejeita_requisicao_sem_arquivo(self):
        response = self.client.post(self.url, {"pasta": "imoveis"})
        self.assertEqual(response.status_code, 400)

    def test_rejeita_arquivo_que_nao_e_imagem(self):
        response = self._enviar(conteudo=b"isto nao e uma imagem", nome="x.jpg")
        self.assertEqual(response.status_code, 400)

    def test_rejeita_arquivo_maior_que_o_limite(self):
        response = self._enviar(conteudo=b"0" * (4 * 1024 * 1024 + 1))
        self.assertEqual(response.status_code, 413)

    def test_salva_imagem_redimensionada_no_storage(self):
        response = self._enviar(conteudo=_imagem_jpeg(3000, 2000))
        self.assertEqual(response.status_code, 200)
        caminho = response.json()["caminho"]
        self.assertTrue(caminho.startswith("imoveis/"))
        self.assertTrue(caminho.endswith(".jpg"))
        with default_storage.open(caminho) as salva:
            self.assertEqual(Image.open(salva).width, 1920)


class ValidarCaminhoImagemTests(TestCase):
    def test_aceita_caminhos_das_pastas_permitidas(self):
        validar_caminho_imagem("imoveis/2026/10/abc123.jpg")
        validar_caminho_imagem("realizacoes/2026/10/abc123.jpg")
        validar_caminho_imagem("perfil/foto-antiga.png")

    def test_rejeita_caminhos_suspeitos(self):
        for valor in ["../segredo.jpg", "imoveis/../../x.jpg", "/etc/passwd", "outra/x.jpg", "imoveis/x.jpg/../y", "imoveis/x"]:
            with self.subTest(valor=valor), self.assertRaises(ValidationError):
                validar_caminho_imagem(valor)


class RealizacaoFormFotoTests(TestCase):
    def test_aceita_caminho_enviado_pelo_upload(self):
        form = RealizacaoForm(data={
            "titulo": "Chave entregue",
            "texto": "",
            "foto": "realizacoes/2026/10/abc123.jpg",
            "visivel": "on",
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["foto"], "realizacoes/2026/10/abc123.jpg")

    def test_exige_foto(self):
        form = RealizacaoForm(data={"titulo": "Chave entregue", "visivel": "on"})
        self.assertFalse(form.is_valid())
        self.assertIn("foto", form.errors)
