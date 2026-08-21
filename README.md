# Corretora de Milhões

Site profissional para uma corretora de imóveis independente: vitrine pública de imóveis, painel de autoatendimento (ela cadastra/edita imóveis, marca como vendido/alugado e posta "negócios fechados"), depoimentos de clientes com moderação, e contato que cai direto no WhatsApp.

Terceiro projeto do portfólio. Meta de entrega: dezembro/2026.

## Stack

- **Python + Django 5** — full-stack em um único framework, com admin, autenticação e ORM prontos. Escolhido por acelerar exatamente a parte mais trabalhosa do projeto (o painel de autoatendimento) sem precisar construir API + front separados.
- **SQLite** em desenvolvimento (zero configuração) → **PostgreSQL** em produção (troca automática via `DATABASE_URL` no `.env`, veja `.env.example`).
- **django-environ** para variáveis de ambiente/segredos fora do código.
- **Pillow** para upload/processamento de imagens.
- **Whitenoise + Gunicorn** para servir estáticos e rodar em produção (Render/Railway/PythonAnywhere — hospedagem ainda não decidida).
- Front-end: templates Django + CSS puro por enquanto (`static/css/style.css`). Dá pra evoluir pra Tailwind ou HTMX depois sem trocar o back-end.

## Estrutura do projeto (apps Django)

| App | Responsabilidade |
|---|---|
| `imoveis` | Modelo central: `Imovel`, `ImovelFoto`, `Realizacao` (posts de negócio fechado). Vitrine pública com busca/filtros e página de detalhe. |
| `perfil` | Dados da corretora: nome, CRECI, bio, região de atuação, WhatsApp, redes sociais, localização do escritório. Desenhado como singleton (só um registro). |
| `depoimentos` | Feedback de clientes externos. Fica pendente até a corretora aprovar no painel — evita spam/reviews falsos. |
| `leads` | Toda submissão do formulário de contato vira um registro aqui (mini-CRM) antes de redirecionar pro WhatsApp com a mensagem pronta. |
| `painel` | Área autenticada da corretora: dashboard, CRUD de imóveis (com upload de várias fotos), troca rápida de status (disponível/reservado/vendido/alugado), publicar "negócio fechado", moderar depoimentos, ver leads. |
| `core` | Home pública (destaques, realizações recentes, depoimentos) e o `context_processor` que injeta os dados da corretora em todo template (navbar, rodapé, botão de WhatsApp flutuante). |

## Telas (mapeadas até agora)

**Público:**
1. Home — destaques, realizações recentes, depoimentos, chamada para vitrine.
2. Vitrine de imóveis (`/imoveis/`) — busca por texto + filtros (negócio, tipo, cidade, bairro, quartos, faixa de valor).
3. Detalhe do imóvel (`/imoveis/<slug>/`) — galeria de fotos, características, mapa (embed Google Maps por lat/long), botão de interesse.
4. Formulário de contato (`/contato/`) — salva o lead e redireciona pro WhatsApp com mensagem pré-preenchida.
5. Novo depoimento (`/depoimentos/novo/`) — cliente externo avalia.

**Painel da corretora** (login obrigatório, `/painel/`):
6. Login.
7. Dashboard — contadores (imóveis, disponíveis, fechados, leads pendentes, depoimentos pendentes) + atalhos.
8. Lista de imóveis com troca rápida de status.
9. Formulário de imóvel (criar/editar) com upload de múltiplas fotos.
10. Confirmação de exclusão.
11. Publicar "negócio fechado" (Realização).
12. Moderar depoimentos (aprovar/excluir).
13. Ver contatos recebidos (leads).

Ainda **não implementado** (próximas iterações — ver Roadmap): comparador de imóveis, área de "imóveis favoritos" para visitantes, notificação automática por WhatsApp/e-mail quando um lead chega, edição de fotos com reordenação por drag-and-drop, blog/conteúdo, timeline pública de conquistas (contagem de negócios fechados em destaque no perfil).

## Modelo de dados (visão geral)

```
PerfilCorretora (singleton)
  nome, foto, creci, bio, regiao_atuacao,
  whatsapp, email, instagram_url, facebook_url,
  endereco_escritorio, latitude, longitude

Imovel
  titulo, slug, codigo_referencia, descricao,
  tipo_negocio [venda|aluguel|venda_aluguel],
  tipo_imovel [apartamento|casa|casa_condominio|terreno|comercial|rural|cobertura|outro],
  status [disponivel|reservado|vendido|alugado|inativo],
  valor, valor_condominio, valor_iptu,
  area_construida, area_terreno, quartos, suites, banheiros, vagas_garagem,
  cidade, bairro, endereco, cep, latitude, longitude,
  destaque, video_url, criado_em, atualizado_em

ImovelFoto  (N:1 com Imovel)
  imovel_id, imagem, legenda, ordem

Realizacao  (N:1 opcional com Imovel — "negócio fechado")
  imovel_id (nullable), titulo, texto, foto, publicado_em, visivel

Depoimento  (N:1 opcional com Imovel)
  nome_cliente, email_cliente, texto, nota (1-5),
  imovel_relacionado_id, aprovado, criado_em

Lead  (N:1 opcional com Imovel)
  nome, telefone, email, mensagem,
  imovel_relacionado_id, atendido, criado_em
```

Todos os relacionamentos com `Imovel` usam `on_delete=SET_NULL` (exceto as fotos, que são `CASCADE`) — assim, excluir um imóvel não apaga o histórico de leads/depoimentos/realizações ligados a ele.

## Rodando localmente

```bash
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env           # ajuste SECRET_KEY se quiser

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

- Site público: http://127.0.0.1:8000/
- Painel da corretora: http://127.0.0.1:8000/painel/login/
- Admin do Django (gestão avançada): http://127.0.0.1:8000/admin/

Antes de qualquer coisa aparecer na vitrine, cadastre o `PerfilCorretora` (pelo `/admin/` por enquanto) e alguns imóveis pelo painel.

## Roadmap sugerido

1. Cadastrar o perfil real da corretora + 3-5 imóveis de exemplo com fotos.
2. Refinar o design (cores, tipografia, fotos de verdade) com identidade visual própria.
3. Notificação automática (e-mail ou WhatsApp Business API) quando um lead novo chega.
4. Área de favoritos para visitantes (sem precisar de conta, via sessão).
5. Timeline pública de conquistas no perfil (nº de negócios fechados, tempo de atuação).
6. Deploy (Render/Railway) + domínio próprio + Postgres gerenciado.
7. Testes automatizados (pytest-django) para os fluxos de contato e cadastro de imóvel.

## Referências de mercado usadas na concepção

Tecimob, Jetimob, Imobzi, Meu Site Imobiliário, Seu Corretor Online, e o site reidosimoveismc.com.br como benchmark de vitrine (filtros, favoritos, depoimentos, vídeos).
