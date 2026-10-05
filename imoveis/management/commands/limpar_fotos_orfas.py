from datetime import timedelta

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.utils import timezone

from imoveis.models import ImovelFoto, Realizacao
from perfil.models import PerfilCorretora

PASTAS = ("imoveis", "realizacoes", "perfil")
IDADE_MINIMA = timedelta(hours=24)


def _arquivos_na_pasta(pasta):
    pendentes = [pasta]
    while pendentes:
        atual = pendentes.pop()
        pastas, arquivos = default_storage.listdir(atual)
        for nome in arquivos:
            yield f"{atual}/{nome}"
        pendentes.extend(f"{atual}/{nome}" for nome in pastas)


def _caminhos_em_uso():
    em_uso = set(ImovelFoto.objects.values_list("imagem", flat=True))
    em_uso |= set(Realizacao.objects.values_list("foto", flat=True))
    em_uso |= set(PerfilCorretora.objects.values_list("foto", flat=True))
    return {caminho for caminho in em_uso if caminho}


class Command(BaseCommand):
    help = (
        "Lista (ou apaga, com --apagar) arquivos de foto no storage que não são "
        "usados por nenhum registro. Ignora arquivos com menos de 24h."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--apagar",
            action="store_true",
            help="Apaga os arquivos. Sem essa opção, só lista o que seria apagado.",
        )

    def handle(self, *args, apagar=False, **options):
        em_uso = _caminhos_em_uso()
        limite = timezone.now() - IDADE_MINIMA
        orfaos = []
        for pasta in PASTAS:
            try:
                arquivos = list(_arquivos_na_pasta(pasta))
            except FileNotFoundError:
                continue
            for caminho in arquivos:
                if caminho in em_uso:
                    continue
                if default_storage.get_modified_time(caminho) > limite:
                    continue
                orfaos.append(caminho)

        for caminho in orfaos:
            self.stdout.write(caminho)

        if not apagar:
            self.stdout.write(
                f"\n{len(orfaos)} arquivo(s) sem uso. Nada foi apagado. "
                "Rode com --apagar para remover."
            )
            return

        for caminho in orfaos:
            default_storage.delete(caminho)
        self.stdout.write(self.style.SUCCESS(f"{len(orfaos)} arquivo(s) apagado(s)."))
