import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Cria a conta única da corretora a partir de variáveis de ambiente.

    Pensado para rodar no build do Render (sem shell interativo, que só
    existe nos planos pagos): lê DJANGO_SUPERUSER_USERNAME/EMAIL/PASSWORD
    e só cria o usuário se ele ainda não existir, então é seguro deixar
    esse comando em todo deploy. Não expõe nenhuma rota nem formulário —
    é só um script de servidor, o site continua sem cadastro público.
    """

    help = "Cria a conta da corretora via DJANGO_SUPERUSER_* se ela ainda não existir."

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not username or not password:
            self.stdout.write(
                "DJANGO_SUPERUSER_USERNAME/PASSWORD não definidos — pulando."
            )
            return

        User = get_user_model()
        if User.objects.filter(username=username).exists():
            self.stdout.write(f"Conta '{username}' já existe — nada a fazer.")
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Conta '{username}' criada."))
