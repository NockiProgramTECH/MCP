# OpenClaw MCP Server

Serveur MCP Python destiné à connecter OpenClaw à des APIs externes de manière modulaire et sécurisée.

> L'intégration GitHub est disponible. Les intégrations sociales seront ajoutées dans les prochaines étapes.

## Développement local

Le projet requiert Python 3.13+ et [uv](https://docs.astral.sh/uv/).

```bash
uv sync
cp .env.example .env
uv run python -m openclaw_mcp
```

Le serveur utilise le transport MCP `stdio`, adapté à un client local comme OpenClaw. Les messages MCP utilisent stdin/stdout ; les logs vont sur stderr.

## Vérifications

```bash
uv run pytest
uv run ruff check .
uv run mypy src
```

## Configuration

Les variables d'environnement sont chargées par Pydantic Settings. Configurez `GITHUB_TOKEN` pour GitHub, `META_ACCESS_TOKEN` pour les Pages Facebook et `INSTAGRAM_ACCESS_TOKEN` pour Instagram. Les tokens doivent rester hors du dépôt. Voir `.env.example`.

## Facebook et Instagram

Les outils Meta utilisent uniquement l'API Graph officielle sur `graph.facebook.com`.

Facebook expose `facebook_get_pages`, `facebook_get_page`, `facebook_create_page_post` et `facebook_get_page_posts`. La publication nécessite un Page access token obtenu en interne via `/me/accounts`; ce token n'est jamais retourné par le serveur. Les permissions Meta généralement nécessaires sont `pages_show_list`, `pages_read_engagement`, `pages_manage_metadata` et `pages_manage_posts`, selon la version et la validation de votre application.

Instagram expose `instagram_get_profile`, `instagram_get_media`, `instagram_create_media_container` et `instagram_publish_media`. Ces outils ciblent les comptes Instagram professionnels éligibles, pas les comptes personnels. Il faut généralement une application Meta, un compte professionnel relié à une Page Facebook, un access token et les permissions `instagram_basic` et `instagram_content_publish`. Les URLs image ou vidéo doivent être publiques et accessibles en HTTPS par Meta. Le serveur ne télécharge pas ces fichiers et ne fait aucun scraping.

La publication Instagram se déroule en deux étapes :

```text
instagram_create_media_container
→ instagram_publish_media
```

La première étape crée un container mais ne publie pas encore le contenu. `instagram_publish_media` est une action réelle et est explicitement signalée comme telle dans sa description MCP.

## Structure

```text
src/openclaw_mcp/
├── config.py       # Configuration validée depuis l'environnement
├── server.py       # Création et démarrage du serveur MCP
├── __main__.py     # Point d'entrée python -m
└── core/
    ├── errors.py   # Erreurs applicatives publiques
    ├── http.py     # Client HTTP partagé et retries bornés
    ├── logging.py  # Logs stderr sans secrets
    └── security.py # Validation des URLs externes
```

## Sécurité

- aucun secret n'est codé en dur ;
- les logs sont envoyés sur stderr afin de ne pas corrompre stdio MCP ;
- les erreurs exposées aux clients ne contiennent pas de traceback ;
- les intégrations vérifient leur configuration avant tout appel externe.
