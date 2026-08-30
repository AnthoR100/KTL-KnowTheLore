# KnowTheLore

Chatbot RAG local spécialisé dans le lore de League of Legends / Runeterra. Le bot ("Le Conteur Légendaire") répond aux questions des fans en s'appuyant exclusivement sur des sources officielles et communautaires vérifiées (Riot Universe, Data Dragon, transcriptions YouTube), avec citations systématiques.

Voir [cdc.md](cdc.md) pour le cahier des charges technique complet (architecture, pipeline RAG, planning, prompts système).

## Stack

- **Backend** : Python 3.12+ / Poetry, FastAPI, SQLAlchemy
- **Base de données** : PostgreSQL + pgvector (embeddings vectoriels)
- **Frontend** : React + Vite
- **LLM local** : Ollama (Llama 3.1 8B / Mistral 7B)
- **Embeddings** : sentence-transformers

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
```

Prérequis : PostgreSQL 15+ avec l'extension `pgvector`, et Ollama avec un modèle téléchargé (voir [cdc.md](cdc.md) pour les détails d'installation et de configuration).

## Conformité

Projet respectant la Riot Fan Content Policy : sources officielles uniquement, attribution systématique, pas de monétisation.

*League of Legends, Legends of Runeterra et leurs logos sont des marques de Riot Games.*
