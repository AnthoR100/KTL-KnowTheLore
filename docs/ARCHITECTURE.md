# KnowTheLore — Architecture technique

> Comment le système est construit, de la source de lore jusqu'à la réponse du chatbot.
> Doc complémentaire au manuel de réglage (`REGLAGES.md`) et au journal de décisions (`DECISIONS.md`).

**État décrit :** cœur RAG fonctionnel (ingestion + retrieval + génération) sur le corpus des biographies de champions, en local.

**Avertissement :** ce document décrit l'état réel et assumé du système, y compris ses limites. Rien ici ne garantit l'absence d'erreurs résiduelles ; les points incertains sont signalés.

---

## 1. Vue d'ensemble : le flux de données

Le système se lit en deux grandes phases.

**Phase A — Ingestion (faite une fois, hors ligne) :** transformer le lore brut en une base interrogeable par le sens.

```
Fiches Universe (JSON brut)         data/raw/universe_champions/*.json
        │
        ▼  parser.py        nettoie le HTML, extrait la biographie + métadonnées
   ParsedDocument (texte propre, en mémoire)
        │
        ▼  chunker.py       découpe en morceaux (paragraphes -> phrases)
   liste de Chunks
        │
        ▼  embedder.py      chaque chunk -> vecteur 1024 via BGE-M3 (Ollama)
   vecteurs
        │
        ▼  ingest.py        insertion atomique en base
   PostgreSQL : documents + chunks + embeddings
```

**Phase B — Interrogation (à chaque question, en ligne) :** retrouver les bons passages et formuler une réponse ancrée.

```
Question (texte)
        │
        ▼  embedder.py      question -> vecteur 1024 (même modèle BGE-M3)
        │
        ▼  retriever.py     recherche par distance cosinus dans pgvector
   k chunks les plus proches (+ leurs sources)
        │
        ▼  generator.py     réordonne les chunks, assemble un contexte
        │                   + prompt système anti-hallucination
        ▼  Ollama (llama3.1:8b)  rédige la réponse à partir du contexte
   Réponse + sources
```

Principe directeur : **le LLM ne répond pas depuis ses connaissances, mais depuis les passages qu'on lui fournit.** C'est ce qui distingue le RAG d'un chatbot généraliste, et ce qui rend la réponse traçable.

---

## 2. La base de données

Trois tables liées, plus une vue de confort. Modèle « document → chunks → embeddings ».

**`documents`** — une ligne par source de lore (un champion = un document).
Champs clés : `source_type` (`riot_universe`), `source_url` (unique), `title`, `raw_content` (le JSON brut entier, archivé), `metadata` (JSONB : champions, régions, etc.), `is_official`, `is_canon`.

**`chunks`** — les morceaux de texte découpés, liés à leur document.
Champs clés : `document_id` (référence), `chunk_index` (position dans le document), `content` (le texte), `token_count` (estimation), `metadata`.
Contrainte : `UNIQUE(document_id, chunk_index)`.

**`embeddings`** — un vecteur par chunk.
Champs clés : `chunk_id` (référence, unique), `vector vector(1024)`, `model_name` (`bge-m3`).

**Relations et intégrité.** Les suppressions cascadent : supprimer un document supprime ses chunks, et supprimer un chunk supprime son embedding (`ON DELETE CASCADE`). On ne peut donc pas avoir un embedding orphelin.

**`chunks_with_sources`** — une vue qui pré-joint `chunks` et `documents`, pratique pour récupérer un chunk avec le contexte de sa source en une requête.

**Pas d'index vectoriel actuellement.** Pour ~581 vecteurs, PostgreSQL parcourt tout en séquentiel (quelques millisecondes) — c'est exact et assez rapide. Un index (IVFFlat ou HNSW), correctement calibré, deviendra utile quand le corpus dépassera plusieurs milliers de vecteurs.

---

## 3. Les composants

### Scraping (hors pipeline applicatif)
Deux sources Riot, récupérées par des scripts séparés produisant des JSON dans `data/raw/`.
- **Data Dragon** (`riot_scraper.py`) : API officielle, lore court. **Abandonné comme source de contenu** (trop résumé), conservé éventuellement comme filet.
- **Universe** (`universe-meeps...`) : API JSON interne découverte via inspection réseau ; fournit la biographie complète (`biography.full`) et la région. C'est la source retenue.

### `parser.py` — nettoyage et extraction
Lit une fiche Universe, extrait `champion.biography.full`, puis : transforme les `</p>` en sauts de paragraphe, retire **toute** balise HTML (robuste aux balises imprévues), décode les entités (`&nbsp;`…), neutralise les espaces insécables, normalise les espaces en préservant les paragraphes. Produit un `ParsedDocument` (dataclass typée). Renvoie `None` si la biographie est vide (garde-fou).

### `chunker.py` — découpage
Découpe hiérarchique : on regroupe par paragraphes ; un paragraphe trop long est redécoupé par phrases. On vise `chunk_size` sans le dépasser, avec un `overlap` entre chunks. Préserve la lisibilité (pas de coupe en plein milieu d'une phrase quand on peut l'éviter). Un texte plus court que `chunk_size` reste un seul chunk.

### `embedder.py` — vectorisation
Appelle Ollama (`/api/embed`) avec BGE-M3. Deux fonctions : `embed_text` (un texte) et `embed_batch` (plusieurs en un appel, bien plus rapide). Garde-fou : lève une erreur si un vecteur ne fait pas exactement 1024 dimensions (incohérence détectée tôt plutôt qu'à l'insertion).

### `ingest.py` / `ingest_all.py` — insertion
`ingest.py` insère un champion (document + chunks + embeddings) dans **une transaction atomique** : tout passe ou rien. Ignore les doublons via `ON CONFLICT (source_url) DO NOTHING` → script rejouable. `ingest_all.py` boucle sur les 173 fiches, chaque champion dans sa propre transaction (un échec isolé n'annule pas les autres), avec un rapport final.

### `retriever.py` — recherche sémantique
Encode la question avec BGE-M3, puis interroge pgvector par distance cosinus (`<=>`), joint les trois tables, et renvoie les `k` chunks les plus proches sous forme d'objets `RetrievedChunk` (texte + titre + source + score + métadonnées). Testable seul, sans LLM — c'est là que se diagnostiquent la plupart des problèmes d'un RAG.

### `generator.py` — génération de la réponse
Récupère les chunks via le retriever, les **réordonne** (par document selon la pertinence, puis par `chunk_index` à l'intérieur d'un document pour respecter l'ordre de lecture), assemble un contexte, et appelle Ollama (`/api/chat`, confirmé fonctionnel) avec un **prompt système** qui impose : répondre uniquement depuis les passages, ne pas inventer, dire « je ne sais pas » si l'info est absente, citer les sources. `temperature` basse (0.2) pour limiter l'invention. Renvoie la réponse + la liste des sources (construite par le code, donc fiable).

---

## 4. La stack technique

- **Python 3.12**, dépendances gérées par **Poetry**.
- **PostgreSQL 18.1** (confirmé via `SELECT version()`) + extension **pgvector 0.8.1** : stockage et recherche vectorielle.
- **Ollama** (service local) servant deux modèles :
  - **`bge-m3`** (multilingue, 1024 dim, contexte 8192 tokens) pour les embeddings ;
  - **`llama3.1:8b`** pour la génération.
- Configuration centralisée dans `.env` (variables d'environnement), lues par les modules → approche « docker-friendly » pour un futur déploiement.

---

## 5. Mécanismes de fiabilité

Le projet vise des réponses fiables et sourcées. Les garde-fous en place :

- **Ancrage dans les sources** : le LLM répond depuis le contexte fourni, pas depuis ses connaissances.
- **Prompt système anti-hallucination** : consigne explicite de dire « je ne sais pas » plutôt que d'inventer. Renforcé le 30/08/2026 suite à une évaluation manuelle (voir `eval/`) qui a révélé deux angles morts : (1) le LLM répondait parfois depuis ses connaissances générales sur League of Legends plutôt que depuis les passages fournis, même sur des faits factuellement exacts (ex. vainqueurs des Worlds) — désormais explicitement interdit ; (2) sur les questions de décompte/liste par tag (« combien de champions Assassin ? »), le LLM inventait un chiffre ou une liste précise sans base dans le contexte — une règle dédiée l'interdit désormais. *Nette amélioration mesurée sur les cas de re-test (voir « Limites connues » ci-dessous pour ce qui reste imparfait).*
- **Température basse** : limite la tendance du LLM à broder.
- **Étiquetage des sources** (`is_official` / `is_canon` / `metadata`) : permettra de distinguer canon et théorie communautaire (voir évolutions).
- **Transactions atomiques** : jamais de document inséré sans ses embeddings.
- **Garde-fou de dimension** : un vecteur incohérent est rejeté à la source.
- **Traçabilité** : les sources affichées sont calculées par le code, pas déclarées par le LLM.

**Limite fondamentale à garder en tête :** aucun de ces mécanismes ne garantit **zéro hallucination**. Un LLM peut inventer même avec un bon prompt et un bon contexte. On réduit fortement le risque ; on ne l'élimine pas.

---

## 6. Limites connues et incertitudes

- **`source_url` Universe** construite par déduction : format à confirmer en navigateur.
- **`num_ctx` du LLM** : valeur par défaut inconnue sur cette version d'Ollama ; risque de troncature silencieuse du contexte si elle est basse (voir `REGLAGES.md`). À vérifier.
- **Tokens estimés** (`token_count`, `chunk_size`) : approximation caractères/4, non garantie.
- **Scores de similarité** : difficilement interprétables dans l'absolu ; juger surtout le classement relatif.
- **Recouvrement** des chunks : peut commencer au milieu d'un mot (raffinement reporté).
- **Découpage en phrases** : regex grossière, peut se tromper sur « M. Yi », « 3.5 ».
- **Corpus** : biographies de champions **et régions** ingérées (173 champions, 13 régions — confirmé via `eval/` et les chunks d'index `internal://index/*`). Les stories Universe et les vidéos communautaires ne sont pas encore ingérées.
- **Décomptes/listes par tag de rôle (Tank, Assassin, Mage, Fighter...)** : aucun chunk d'index ne les calcule (`build_index_chunk.py` ne couvre que régions et champions). Le prompt renforcé du 30/08/2026 a réduit mais **pas éliminé** le risque : le LLM peut encore produire une liste de noms non présents dans les chunks retournés, parfois assortie d'un aveu d'incomplétude qui n'empêche pas la fabrication en amont (constaté sur les tags Tank et Mage/Fighter lors du re-test). À day one, éviter de présenter ces réponses comme fiables sans vérification manuelle.
- **Filtrage de champions par région (agrégats)** : le retriever ne fait qu'une recherche sémantique top-k, pas un filtre SQL sur la métadonnée `regions` — une question du type « quels champions sont associés à Ionia ? » renvoie une liste plausible mais structurellement non exhaustive (constaté : Karma, Shen absents pour Ionia ; Katarina, LeBlanc absents pour Noxus lors du test).
- **Fidélité au passage récupéré sur les cas dramatiques/ambigus** : constaté sur le cas Kayn/Rhaast — le LLM a affirmé à deux reprises, avec assurance, que « Rhaast a pris le contrôle de Kayn », alors que le chunk réellement récupéré indique l'inverse (« Kayn n'avait aucune intention de se laisser si facilement dominer. Fort de son triomphe... »). C'est un échec de fidélité au texte fourni, distinct du recours aux connaissances générales — le prompt renforcé ne le couvre pas explicitement à ce jour.
- **Chronologie de récits complexes multi-documents** (ex. Yasuo/Yone) : le LLM peut encore mélanger l'ordre des événements ou inverser qui a tué qui, même sans inventer de nom absent du contexte.

*Ces limites sont documentées après une évaluation manuelle sur 35 questions couvrant lore simple, lore ambigu, questions agrégées et hors-scope — voir `eval/questions.json` et `eval/run_eval.py`.*

---

## 7. Évaluation

Un harnais de test manuel vit dans `eval/` (pas de `tests/` automatisés à ce jour — le scoring automatique d'une réponse en langue naturelle n'est pas fiable, la vérification reste volontairement manuelle) :

- **`eval/questions.json`** : 35 questions réparties en 4 familles — `lore_simple`, `lore_ambigu` (cas volontairement ambigus ou multi-documents, ex. Yasuo/Yone, Kayn/Rhaast), `questions_agregees` (décomptes, listes, filtrage par région/tag), `hors_lore` (doit être refusé).
- **`eval/run_eval.py`** : rejoue les questions contre le pipeline réel (`retriever` + `generator`) et écrit un rapport Markdown dans `eval/results/` avec réponse générée, sources retournées, et cases à cocher pour une vérification manuelle (`--category`, `--id`, `--retrieval-only`, `--k`).

Premier passage complet le 30/08/2026 : a directement motivé le renforcement du `SYSTEM_PROMPT` décrit en section 5. Les limites qui en découlent sont listées en section 6.

---

## 8. Évolutions prévues

- **Stories Universe** : nouvelle catégorie de documents (le `source_type` l'anticipe déjà) — les régions, elles, sont déjà ingérées.
- **Contenu communautaire (vidéos type « bubule »)** : à ingérer avec nettoyage des noms propres, et **tagué comme théorie** (non officiel).
- **Génération consciente du niveau de fiabilité** : le générateur passera au prompt le statut (officiel vs théorie) de chaque chunk, pour formuler différemment — « selon le lore officiel… » vs un ton spéculatif assumé pour les théories. *Règle : une théorie ne s'affiche que si un chunk communautaire réel a été récupéré ; jamais une invention du LLM déguisée.*
- **Interface** : aujourd'hui en ligne de commande ; une API (FastAPI) puis éventuellement un front pourront s'y brancher.
- **Déploiement VPS** : à dimensionner après mesure de la consommation réelle.
- **Index vectoriel** : à réintroduire, calibré, quand le volume grossira.

---

*Document vivant : à mettre à jour à mesure que le système évolue. Les limites listées ne sont pas des défauts à cacher mais des points de vigilance assumés.*
