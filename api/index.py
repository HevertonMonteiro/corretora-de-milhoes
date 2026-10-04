import json

from config.wsgi import application as _app


def app(environ, start_response):
    if environ.get("PATH_INFO", "").startswith("/diagnostico-ambiente"):
        dados = {
            k: str(v)
            for k, v in environ.items()
            if k.startswith(("HTTP_X", "PATH", "REQUEST", "SCRIPT", "QUERY", "wsgi.url"))
        }
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(dados, indent=1).encode()]
    return _app(environ, start_response)
