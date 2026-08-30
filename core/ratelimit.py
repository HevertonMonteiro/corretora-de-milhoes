from functools import wraps

from django.core.cache import cache
from django.http import HttpResponse


def _ip_do_cliente(request):
    encaminhado = request.META.get("HTTP_X_FORWARDED_FOR")
    if encaminhado:
        return encaminhado.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def limitar_por_ip(chave, max_tentativas=5, janela_segundos=300):
    """Limita quantos POSTs o mesmo IP pode enviar a uma view dentro de uma
    janela de tempo — proteção simples contra spam e força bruta em
    formulários públicos, sem depender de serviço externo (usa o cache
    padrão do Django)."""

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if request.method == "POST":
                cache_key = f"ratelimit:{chave}:{_ip_do_cliente(request)}"
                tentativas = cache.get(cache_key, 0)
                if tentativas >= max_tentativas:
                    return HttpResponse(
                        "Muitas tentativas em pouco tempo. Aguarde alguns "
                        "minutos e tente novamente.",
                        status=429,
                    )
                cache.set(cache_key, tentativas + 1, janela_segundos)
            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator
