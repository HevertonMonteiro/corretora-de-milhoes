from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import PerfilCorretora


class PerfilCorretoraModelTests(TestCase):
    def test_whatsapp_numero_limpo_adiciona_codigo_do_brasil(self):
        perfil = PerfilCorretora(
            nome="Ana Corretora",
            creci="PE 12345",
            regiao_atuacao="Recife e região",
            whatsapp="(81) 99999-9999",
        )
        self.assertEqual(perfil.whatsapp_numero_limpo, "5581999999999")

    def test_whatsapp_numero_limpo_mantem_codigo_ja_presente(self):
        perfil = PerfilCorretora(
            nome="Ana Corretora",
            creci="PE 12345",
            regiao_atuacao="Recife e região",
            whatsapp="+55 81 99999-9999",
        )
        self.assertEqual(perfil.whatsapp_numero_limpo, "5581999999999")

    def test_nao_permite_criar_um_segundo_perfil(self):
        PerfilCorretora.objects.create(
            nome="Ana Corretora",
            creci="PE 12345",
            regiao_atuacao="Recife e região",
            whatsapp="5581999999999",
        )
        segundo = PerfilCorretora(
            nome="Outra Corretora",
            creci="PE 54321",
            regiao_atuacao="Olinda",
            whatsapp="5581988887777",
        )
        with self.assertRaises(ValidationError):
            segundo.full_clean()
