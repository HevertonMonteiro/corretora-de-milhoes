from django.test import TestCase
from django.urls import reverse

from .models import Imovel


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
