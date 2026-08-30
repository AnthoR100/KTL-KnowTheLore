# KnowTheLore

Chatbot RAG local spécialisé dans le lore de League of Legends / Runeterra. Le bot ("Le Conteur Légendaire") répond aux questions des fans en s'appuyant exclusivement sur des sources officielles et communautaires vérifiées (Riot Universe, Data Dragon, transcriptions YouTube), avec citations systématiques.

Voir `docs/ARCHITECTURE.md` pour le détail de l'architecture et du pipeline RAG (note : `docs/` est un dossier de notes perso, non versionné — disponible en local uniquement).

## Stack

- **Backend** : Python 3.12+ / Poetry, FastAPI, SQLAlchemy
- **Base de données** : PostgreSQL + pgvector (embeddings vectoriels, 1024 dimensions)
- **Frontend** : React + Vite
- **LLM local** : Ollama (`llama3.1:8b` pour la génération, `bge-m3` pour les embeddings)

## Structure du projet

```
src/knowthelore/   Backend (ingestion, accès base de données)
models/            Modèles SQLAlchemy (documents, chunks, embeddings)
scraping/          Scripts de scraping (bios champions, régions)
frontend/          Interface chat (React + Vite)
schema.sql         Schéma PostgreSQL (extension pgvector, tables, index, vue)
data/raw/          Données scrapées brutes (JSON)
```

## Démarrage

```bash
poetry install
cp .env.example .env  # puis renseigner DATABASE_URL et les autres variables
```

Prérequis : PostgreSQL avec l'extension `pgvector`, et Ollama avec les modèles `llama3.1:8b` et `bge-m3` téléchargés.

## Conformité

Projet respectant la Riot Fan Content Policy : sources officielles uniquement, attribution systématique, pas de monétisation.

*League of Legends, Legends of Runeterra et leurs logos sont des marques de Riot Games.*
