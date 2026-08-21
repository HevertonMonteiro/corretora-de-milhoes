from perfil.models import PerfilCorretora


def perfil_corretora(request):
    """Disponibiliza os dados da corretora (nome, WhatsApp, redes sociais)
    em todos os templates — usado no navbar, rodapé e botão flutuante de
    WhatsApp, sem precisar repetir a consulta em cada view."""
    return {"perfil": PerfilCorretora.objects.first()}
