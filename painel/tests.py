from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


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
