# KnowTheLore

Chatbot RAG local spécialisé dans le lore de League of Legends / Runeterra. Le bot ("Aldric") répond aux questions des fans en s'appuyant exclusivement sur des sources officielles vérifiées (biographies et régions Riot Universe), avec citations systématiques. Les transcriptions YouTube sont envisagées comme source future, pas encore ingérées.

Voir `docs/ARCHITECTURE.md` pour l'architecture et le pipeline RAG, `docs/DECISIONS.md` pour l'historique des choix techniques et leurs justifications, et `docs/REGLAGES.md` pour le détail des paramètres (chunking, retrieval, génération).

## Stack

- **Backend** : Python 3.12+ / Poetry, FastAPI
- **Base de données** : PostgreSQL + pgvector (embeddings vectoriels, 1024 dimensions), accédée en SQL brut via `psycopg` (v3). SQLAlchemy est déclaré en dépendance et utilisé dans `models/` à titre d'exercice, mais n'est pas branché sur le pipeline RAG réel (aucun moteur SQLAlchemy n'y est créé).
- **Frontend** : React + Vite
- **LLM local** : Ollama (`llama3.1:8b` pour la génération, `bge-m3` pour les embeddings)

## Structure du projet

```
src/knowthelore/   Backend (ingestion, retrieval, génération, API FastAPI)
eval/              Jeu de questions + script d'évaluation manuelle du pipeline RAG
migrations/        Scripts de migration de schéma ponctuels
models/            Exercice SQLAlchemy (non branché sur le pipeline réel)
scraping/          Scripts de scraping (bios champions, régions)
frontend/          Interface chat (React + Vite)
schema.sql         Schéma PostgreSQL (extension pgvector, tables, index, vue)
docs/              Architecture, décisions, réglages (voir liens ci-dessus)
data/raw/          Données scrapées brutes (JSON, non versionné)
```

## Démarrage

```bash
poetry install
cp .env.example .env  # puis renseigner DATABASE_URL et les autres variables
```

Prérequis : PostgreSQL avec l'extension `pgvector`, et Ollama avec les modèles `llama3.1:8b` et `bge-m3` téléchargés.

## Lancer le projet

```bash
# Ingestion complète (corpus champions + régions + index agrégé)
poetry run python -m knowthelore.ingestion.ingest_full

# Reconstruire l'index agrégé seul, après une modification du corpus
poetry run python -m knowthelore.ingestion.build_index_chunk --write

# API
poetry run uvicorn knowthelore.api.main:app --reload

# Frontend
cd frontend && npm run dev
```

## Conformité

Projet respectant la Riot Fan Content Policy : sources officielles uniquement, attribution systématique, pas de monétisation.

*League of Legends, Legends of Runeterra et leurs logos sont des marques de Riot Games.*
