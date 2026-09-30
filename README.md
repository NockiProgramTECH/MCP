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

Les variables d'environnement sont chargées par Pydantic Settings. Les tokens ne sont pas encore consommés par le socle et doivent rester hors du dépôt. Voir `.env.example`.

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
