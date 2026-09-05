from django.test import TestCase
from django.urls import reverse

from .models import Lead


class ContatoViewTests(TestCase):
    def test_get_retorna_formulario(self):
        response = self.client.get(reverse("leads:contato"))
        self.assertEqual(response.status_code, 200)

    def test_post_valido_cria_lead_e_mostra_sucesso(self):
        response = self.client.post(reverse("leads:contato"), {
            "nome": "Maria Cliente",
            "telefone": "81999998888",
            "email": "",
            "mensagem": "Tenho interesse nesse imóvel.",
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "leads/sucesso.html")
        self.assertEqual(Lead.objects.count(), 1)

    def test_post_invalido_nao_cria_lead(self):
        response = self.client.post(reverse("leads:contato"), {"nome": ""})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Lead.objects.count(), 0)


class LeadModelTests(TestCase):
    def test_link_whatsapp_sem_perfil_cadastrado(self):
        lead = Lead.objects.create(nome="João", telefone="81988887777")
        link = lead.link_whatsapp()
        self.assertTrue(link.startswith("https://wa.me/"))
