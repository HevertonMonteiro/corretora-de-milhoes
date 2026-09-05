from django.test import TestCase
from django.urls import reverse

from imoveis.models import Imovel


class HomeViewTests(TestCase):
    def test_home_carrega_sem_imoveis(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_home_mostra_imovel_em_destaque(self):
        Imovel.objects.create(
            titulo="Apartamento na praia",
            tipo_negocio=Imovel.TipoNegocio.VENDA,
            tipo_imovel=Imovel.TipoImovel.APARTAMENTO,
            valor="350000.00",
            cidade="Recife",
            bairro="Boa Viagem",
            destaque=True,
        )
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["imoveis_destaque"]), 1)
