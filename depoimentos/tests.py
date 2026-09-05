from django.test import TestCase
from django.urls import reverse

from .models import Depoimento


class NovoDepoimentoViewTests(TestCase):
    def test_get_retorna_formulario(self):
        response = self.client.get(reverse("depoimentos:novo"))
        self.assertEqual(response.status_code, 200)

    def test_post_valido_cria_depoimento_pendente_de_aprovacao(self):
        response = self.client.post(reverse("depoimentos:novo"), {
            "nome_cliente": "Cliente Satisfeito",
            "email_cliente": "",
            "texto": "Atendimento excelente, recomendo muito!",
            "nota": 5,
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        depoimento = Depoimento.objects.get()
        self.assertFalse(depoimento.aprovado)

    def test_post_com_nota_fora_do_intervalo_e_invalido(self):
        response = self.client.post(reverse("depoimentos:novo"), {
            "nome_cliente": "Cliente",
            "texto": "Texto qualquer",
            "nota": 6,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Depoimento.objects.count(), 0)
