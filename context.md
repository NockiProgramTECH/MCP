# Mission

Tu es un ingénieur logiciel senior spécialisé en :

* Python 3.13+
* MCP (Model Context Protocol)
* FastAPI
* Pydantic
* sécurité des API
* architecture logicielle
* agents IA
* OpenClaw
* automatisation
* OAuth 2.0
* APIs REST
* Docker

Je veux que tu construises un **serveur MCP complet en Python**, propre, sécurisé, extensible et réellement utilisable par **OpenClaw**.

Ne crée pas un simple exemple pédagogique.

Je veux un véritable projet que je peux installer localement, lancer et connecter à OpenClaw.

---

# 1. Objectif du serveur

Le serveur doit servir de couche MCP entre OpenClaw et mes différents services.

Architecture cible :

```text
                    ┌─────────────────────┐
                    │      OpenClaw       │
                    │       Agent IA      │
                    └──────────┬──────────┘
                               │
                         MCP Protocol
                               │
                               ▼
                    ┌─────────────────────┐
                    │     MCP Server      │
                    │       Python        │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
          Social APIs       GitHub API       Custom APIs
              │                │                │
              ▼                ▼                ▼
         LinkedIn          GitHub          Mes services
         Facebook
         Instagram
         TikTok
```

Le serveur MCP doit être conçu de manière modulaire afin que je puisse ajouter de nouveaux services plus tard sans réécrire toute l'application.

---

# 2. Stack obligatoire

Utilise :

* Python 3.13+
* MCP Python SDK officiel
* Pydantic v2
* httpx
* python-dotenv
* pytest
* Ruff
* mypy
* uv pour la gestion du projet

Utilise une architecture moderne et typée.

Évite les dépendances inutiles.

Ne crée pas de framework maison.

---

# 3. Structure du projet

Crée une structure similaire à :

```text
openclaw-mcp/
│
├── pyproject.toml
├── README.md
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
│
├── src/
│   └── openclaw_mcp/
│       ├── __init__.py
│       ├── server.py
│       ├── config.py
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── security.py
│       │   ├── errors.py
│       │   └── http.py
│       │
│       ├── models/
│       │   ├── __init__.py
│       │   ├── social.py
│       │   └── common.py
│       │
│       ├── services/
│       │   ├── __init__.py
│       │   ├── github.py
│       │   ├── linkedin.py
│       │   ├── facebook.py
│       │   ├── instagram.py
│       │   └── tiktok.py
│       │
│       └── tools/
│           ├── __init__.py
│           ├── github.py
│           ├── linkedin.py
│           ├── facebook.py
│           ├── instagram.py
│           └── tiktok.py
│
└── tests/
    ├── __init__.py
    ├── test_config.py
    ├── test_github.py
    └── test_social.py
```

Tu peux modifier cette structure si tu as une meilleure architecture, mais explique précisément pourquoi.

---

# 4. MCP

Le serveur doit utiliser correctement le protocole MCP.

Expose clairement :

* tools
* resources si réellement nécessaires
* prompts si réellement nécessaires

Ne simule pas MCP avec de simples endpoints REST.

Le serveur doit être compatible avec un client MCP moderne et notamment utilisable depuis OpenClaw.

---

# 5. Tools

Commence avec les outils suivants.

## GitHub

Créer :

```text
github_get_user
github_list_repositories
github_get_repository
github_create_issue
github_list_issues
github_create_repository
```

Chaque tool doit :

* avoir un nom explicite
* avoir une description claire
* utiliser Pydantic pour ses paramètres
* valider les entrées
* gérer les erreurs API
* ne jamais exposer le token GitHub

---

# 6. LinkedIn

Prépare l'architecture pour :

```text
linkedin_get_profile
linkedin_create_post
linkedin_get_posts
```

Attention :

Ne prétends pas que toutes les opérations sont disponibles publiquement si l'API LinkedIn ne les autorise pas.

Lorsque certaines opérations nécessitent une permission OAuth spécifique, indique-le clairement.

Ne contourne jamais les restrictions de l'API.

---

# 7. Facebook

Prépare :

```text
facebook_get_pages
facebook_get_page
facebook_create_page_post
facebook_get_page_posts
```

Utilise l'API officielle Meta.

Ne demande jamais un mot de passe Facebook.

Utilise uniquement OAuth/access tokens.

---

# 8. Instagram

Prépare :

```text
instagram_get_profile
instagram_get_media
instagram_create_media_container
instagram_publish_media
```

Respecte les restrictions de l'Instagram Graph API.

Ne prétends pas pouvoir publier sur un compte personnel si l'API ne le permet pas.

Explique clairement les prérequis :

* compte professionnel
* page Facebook associée lorsque nécessaire
* permissions
* access token
* App Meta

---

# 9. TikTok

Prépare :

```text
tiktok_get_user
tiktok_get_videos
tiktok_publish_video
```

Utilise uniquement l'API officielle TikTok.

Si une fonctionnalité nécessite une approbation particulière ou une API spécifique, documente-le.

Ne crée aucun mécanisme de scraping.

---

# 10. Authentification

Toutes les informations sensibles doivent venir de variables d'environnement.

Exemple :

```env
GITHUB_TOKEN=

LINKEDIN_ACCESS_TOKEN=

META_ACCESS_TOKEN=

INSTAGRAM_ACCESS_TOKEN=

TIKTOK_ACCESS_TOKEN=
```

Ne mets JAMAIS de token directement dans le code.

Ne mets jamais les tokens dans les logs.

Ne retourne jamais les tokens dans les réponses MCP.

---

# 11. Configuration

Utilise Pydantic Settings.

Exemple :

```python
class Settings(BaseSettings):
    github_token: str | None = None
    linkedin_access_token: str | None = None
    meta_access_token: str | None = None
    instagram_access_token: str | None = None
    tiktok_access_token: str | None = None
```

Les services doivent fonctionner même lorsqu'un autre service n'est pas configuré.

Par exemple :

```text
GitHub configuré
LinkedIn non configuré
Instagram non configuré
```

ne doit pas empêcher le serveur MCP de démarrer.

---

# 12. Sécurité

Je veux une vraie couche de sécurité.

Implémente notamment :

* validation Pydantic
* timeout HTTP
* gestion des erreurs
* limitation raisonnable des requêtes
* aucune fuite de secrets
* logs sans données sensibles
* protection contre les URLs arbitraires si une tool accepte des URLs
* pas de shell arbitraire
* pas d'exécution de code arbitraire
* pas de `eval`
* pas de `exec`
* pas de téléchargement arbitraire de fichiers
* pas de scraping de réseaux sociaux

Pour toute opération destructive ou sensible, ajoute une validation explicite.

---

# 13. HTTP

Centralise les appels HTTP.

Crée par exemple :

```python
HttpClient
```

avec :

* timeout
* headers
* gestion des erreurs
* retries limités lorsque pertinent
* fermeture correcte des connexions

Ne crée pas un `httpx.AsyncClient()` différent dans chaque fonction sans gestion de cycle de vie.

---

# 14. Architecture

Sépare clairement :

```text
MCP Tool
    ↓
Service
    ↓
HTTP Client
    ↓
External API
```

Par exemple :

```text
tools/github.py
        ↓
services/github.py
        ↓
core/http.py
        ↓
GitHub API
```

Les MCP tools ne doivent pas contenir toute la logique métier.

---

# 15. Erreurs

Crée des erreurs propres.

Par exemple :

```text
AuthenticationError
AuthorizationError
ExternalAPIError
ValidationError
RateLimitError
ConfigurationError
```

Les erreurs retournées au modèle doivent être compréhensibles.

Exemple :

```text
GitHub is not configured.
Set GITHUB_TOKEN in the environment.
```

et jamais :

```text
Traceback ...
GITHUB_TOKEN=ghp_xxxxxxxxx
```

---

# 16. Mode lecture / écriture

Fais clairement la distinction entre :

### Lecture

```text
get
list
search
```

et :

### Écriture

```text
create
update
delete
publish
```

Les tools d'écriture doivent avoir des descriptions explicites afin que l'agent IA comprenne qu'elles provoquent une action réelle.

Exemple :

```text
github_create_issue
```

Description :

```text
Creates a real GitHub issue in the specified repository.
This operation modifies external state.
```

---

# 17. OpenClaw

Ajoute une documentation complète expliquant comment connecter le serveur MCP à OpenClaw.

Je veux notamment :

```text
Installation
Configuration
Lancement
Test MCP
Configuration OpenClaw
Variables d'environnement
Dépannage
```

Donne les commandes exactes.

Par exemple :

```bash
uv sync
uv run python -m openclaw_mcp
```

Puis montre précisément comment déclarer le serveur MCP dans OpenClaw.

N'invente pas une syntaxe OpenClaw.

Si la syntaxe dépend de la version d'OpenClaw, indique-le et donne la méthode adaptée à une version récente.

---

# 18. Transport MCP

Utilise un transport MCP adapté à l'utilisation locale avec OpenClaw.

Explique :

* pourquoi ce transport est choisi
* comment le serveur démarre
* comment OpenClaw s'y connecte
* comment tester la connexion

Si plusieurs transports sont pertinents, implémente d'abord le plus simple pour le développement local et documente les autres.

---

# 19. Tests

Crée des tests avec pytest.

Je veux au minimum :

```text
test configuration
test authentication
test GitHub service
test validation
test error handling
```

Les tests ne doivent pas utiliser mes vrais tokens.

Utilise des mocks.

---

# 20. Docker

Ajoute :

```text
Dockerfile
docker-compose.yml
```

Le serveur doit pouvoir fonctionner :

### Localement

```bash
uv run ...
```

### Docker

```bash
docker compose up
```

Les secrets doivent être fournis via `.env`.

Ne copie jamais `.env` dans l'image Docker.

---

# 21. README

Le README doit être extrêmement pratique.

Structure :

```text
# OpenClaw MCP Server

## Features

## Architecture

## Requirements

## Installation

## Environment variables

## GitHub setup

## LinkedIn setup

## Meta setup

## Instagram setup

## TikTok setup

## Running locally

## Running with Docker

## Connecting to OpenClaw

## Testing

## Security

## Troubleshooting

## Adding a new integration
```

Ajoute des exemples réels de commandes.

---

# 22. Ajout futur d'intégrations

L'architecture doit permettre d'ajouter facilement :

```text
Discord
Telegram
Gmail
Google Drive
Notion
Slack
AWS
Cloudflare
Docker
PostgreSQL
MySQL
FastAPI
Django
```

sans modifier le cœur du serveur.

Explique dans le README comment ajouter une nouvelle intégration.

---

# 23. Très important : ne fabrique aucune API

Pour chaque réseau social :

1. Vérifie la documentation officielle si tu as accès au Web.
2. Utilise les endpoints réellement disponibles.
3. Indique les permissions OAuth nécessaires.
4. Indique les restrictions.
5. Ne suppose pas qu'une API existe.
6. Ne crée pas de faux endpoint.
7. Ne mets pas de données fictives présentées comme réelles.

Si tu ne peux pas vérifier une API, indique explicitement :

```text
UNVERIFIED
```

au lieu d'inventer.

---

# 24. Workflow de génération

Ne génère pas tout le projet dans un seul bloc gigantesque.

Travaille en étapes.

### Étape 1

Analyse l'architecture et propose le plan.

### Étape 2

Crée :

```text
pyproject.toml
src/
config
core
server
```

### Étape 3

Implémente GitHub.

### Étape 4

Implémente Meta/Facebook/Instagram.

### Étape 5

Implémente LinkedIn.

### Étape 6

Implémente TikTok.

### Étape 7

Ajoute les tests.

### Étape 8

Ajoute Docker.

### Étape 9

Configure OpenClaw.

### Étape 10

Effectue une revue finale de sécurité.

À chaque étape :

* montre les fichiers créés
* montre leur contenu complet
* explique brièvement leur rôle
* donne les commandes à exécuter
* attends ma validation avant de passer à l'étape suivante.

---

# 25. Règle importante

Je suis développeur Python mais je veux comprendre ce que je construis.

Ne me donne pas seulement du code.

Pour chaque composant important, explique :

```text
Pourquoi ?
Comment ça fonctionne ?
Comment OpenClaw l'utilise ?
Quel risque de sécurité existe ?
Comment le tester ?
```

Utilise des explications simples mais techniquement exactes.

---

# 26. Premier résultat attendu

Commence maintenant par :

1. analyser l'architecture ;
2. identifier les problèmes potentiels ;
3. proposer l'arborescence finale ;
4. proposer les dépendances ;
5. expliquer le fonctionnement du serveur MCP avec OpenClaw ;
6. ne génère PAS encore tout le code.

Attends ensuite ma validation avant de générer le projet.
creer un roadmap pour l'avancer du projet

