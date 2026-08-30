# KnowTheLore — Journal des décisions

> Chatbot RAG sur le lore de League of Legends (univers Runeterra), en français.
> Ce document trace les questions qu'on s'est posées et les décisions prises, avec leur justification.
> Il est volontairement honnête sur les incertitudes : plusieurs choix restent à valider par la mesure.

**Dernière mise à jour :** - Questions agrégées ("combien de régions ?") : **traité (Option D)**. Deux documents index (`source_type='index'`) générés depuis la base par `build_index_chunk.py`, reconstruits en fin de `ingest_full.py`. Décompte inscrit dans le texte. Validé sur quelques phrasés (index rang 1, sans parasiter le lore normal) ; cas limites par région restant à éprouver. Incertitude : le décompte reflète le corpus, pas un canon absolu.
**Statut global :** RAG complet de bout en bout (ingestion → retrieval → génération) exposé par une API HTTP. Prochaine étape : front React ou tests approfondis.

---

## 1. Cadrage du projet

| Sujet | Décision | Justification | Incertitude / à revoir |
|---|---|---|---|
| Périmètre | Backend + base de données + chatbot RAG. Pas de site encyclopédique, pas de carte. | Rester simple et pédagogique. | — |
| Objectif | Réponses fiables et sourcées sur le lore officiel, en français. | Cible francophone d'abord. | — |
| Approche de travail | L'utilisateur code, Claude guide étape par étape ; on valide chaque maillon isolément avant d'assembler. | Apprentissage réel plutôt que livraison opaque. | — |
| Couche « compagnon/personnage » | Reportée. | Pas prioritaire ; le moteur Q&A passe avant. | À reconsidérer plus tard. |

---

## 2. Sources de données

| Sujet | Décision | Justification | Incertitude / à revoir |
|---|---|---|---|
| Politique de sources | Officiel **+** théories communautaires solides, **étiquetées par niveau de fiabilité**. | Ne pas mélanger fait canon et théorie ; le bot doit pouvoir distinguer les deux. | La distinction repose sur `is_official` / `is_canon` / `metadata` — usage précis à formaliser. |
| Data Dragon vs Universe | **Abandon de Data Dragon** comme source de contenu, au profit d'**Universe**. | Le `lore` de Data Dragon est un résumé (~600 car.) ; la `biography.full` d'Universe est le lore complet (~7× plus). | Data Dragon conservé hors pipeline comme filet éventuel (région, repli si bio vide). |
| Langue | Tout en **français** (`fr_FR` / `fr_fr`). | Cible francophone. | — |
| Niveaux de contenu Universe | 1) biographies de champions (fait), 2) descriptions de régions/factions (fait), 3) stories liées (extension future). | Commencer par le plus gros volume déjà disponible. | Stories non encore ingérées. |
| Transcriptions YouTube | Mises de côté pour l'instant. | Transcription Whisper qui dégrade les noms propres (les tokens les plus importants pour du lore) ; nettoyage coûteux. | À réintégrer après le pipeline officiel, avec nettoyage dédié. |
| Conformité Riot | Projet fan-made non commercial ; pas d'assets ; intention de présenter le projet via Riot pour validation. | Réduire le risque lié à la rediffusion de contenu. | Modalités exactes (Fan Content Policy vs portail dev) **non confirmées** ; Claude n'est pas juriste. |

---

## 3. Découverte des API Riot

| Sujet | Décision / constat | Justification | Incertitude / à revoir |
|---|---|---|---|
| Data Dragon | URL `cdn/<version>/data/<locale>/champion/<Nom>.json` ; locale = segment d'URL. | Confirmé : `fr_FR` renvoie bien le lore français (vérifié sur Aatrox). | Version de secours codée en dur dans le scraper (`13.24.1`) = ancienne ; signal d'échec si elle apparaît. |
| Universe — API cachée | Endpoint JSON `universe-meeps.leagueoflegends.com/v1/fr_fr/champions/<slug>/index.json`. | Découvert via un script « espion réseau » (Playwright) ; confirmé par `ahri-full.json`. Pas besoin de navigateur headless pour scraper. | Endpoint non officiel : peut changer sans préavis. |
| Liste des champions | Lue depuis le fichier `search` déjà capturé (173 slugs), pas re-téléchargée. | Évite une dépendance à une URL search non confirmée. | Le fichier est une « photo » ; à rafraîchir pour rester à jour (ex. nouveaux champions). |
| Écart de comptage | Data Dragon = 172 champions, Universe = 173. | Probablement « Norra » (sortie 2026-02-13). | Correspondance exacte des deux sources non vérifiée. |

---

## 4. Pipeline d'ingestion

| Sujet | Décision | Justification | Incertitude / à revoir |
|---|---|---|---|
| Données brutes intouchées | `data/raw/` en lecture seule par convention ; le nettoyage produit des données dérivées, jamais réécrites sur le brut. | Pouvoir tout reconstruire ; ne rien perdre en cas d'erreur. | Pas de dossier `data/processed/` intermédiaire (choix de simplicité). |
| Contenu source | **`biography.full` uniquement** (on ignore `short`, `quote`). | Éviter les doublons de sens dans la base ; `full` = le lore complet. | — |
| Nettoyage HTML | Retirer **toute** balise (`<p>`, `<i>`, et imprévu), décoder les entités (`&nbsp;`...), neutraliser `\xa0`, préserver les paragraphes. | Robustesse : ne pas coder en dur les seules balises vues sur un échantillon. | Vérifié sur 4 champions / 173. Une balise exotique reste possible ailleurs (le code la retirerait quand même). |
| Format de sortie | `dataclass ParsedDocument` (source_type, source_url, title, content, language, is_official, is_canon, metadata). | Conteneur typé = une ligne de la future table `documents`. | `source_url` Universe **construite par déduction**, format non confirmé en navigateur. |
| Région | Extraite de `associated-faction-slug` ; `unaffiliated` → liste vide. | Universe fournit la région que Data Dragon n'avait pas. | — |
| Chunking — unité | Caractères (pas tokens). Découpe hiérarchique : paragraphes d'abord, phrases en secours. | Couper sur les frontières de sens ; ne pas casser les phrases. | Tokens ≈ caractères / 4 : **approximation**, à recalibrer avec le vrai tokenizer. |
| Chunking — taille | `chunk_size=2000`, `overlap=200` caractères (≈ 500/50 tokens), paramétrable. | Valeurs de départ raisonnables, ajustables sans toucher au code. | Taille optimale non mesurée. |
| Recouvrement | Repris en caractères bruts (peut commencer au milieu d'un mot). | Choix pragmatique ; suffisant pour les embeddings. | Raffinement (reprise par phrases entières) reporté ; à faire si le retrieval déçoit. |
| Stats corpus | 173/173 parsés, 0 échec. Longueurs : min 341 (Twitch), max 14918 (Xerath), médiane 4757 car. | Mesuré, pas supposé — a guidé le chunking. | — |

---

## 5. Embeddings

| Sujet | Décision | Justification | Incertitude / à revoir |
|---|---|---|---|
| Modèle | **BGE-M3** (multilingue, 1024 dimensions, contexte 8192 tokens). | Bon support du français ; `all-MiniLM-L6-v2` (prévu initialement) est surtout anglais et mauvais en français (confirmé par recherche + cas documentés). | Gain réel sur **ce** corpus non mesuré ; chiffres de benchmark à prendre avec prudence. |
| Exécution | Via **Ollama** (déjà utilisé pour le LLM). | Un seul outil à maintenir ; projet Python léger (pas de PyTorch) ; léger sur VPS. | API d'embeddings d'Ollama a varié selon versions — **format confirmé sur l'environnement réel** : `/api/embed` → `{"embeddings": [[...]]}`. |
| Batch | Encodage par lots (`input` = liste) validé : plusieurs textes en un appel. | Bien plus rapide que 1 appel par chunk. | — |
| Garde-fou dimension | Le module lève une erreur si un vecteur ≠ 1024. | Échouer tôt et clairement plutôt qu'à l'insertion. | — |
| Lecture de la config | `embedder.py` lit `EMBEDDING_MODEL`/`EMBEDDING_DIM` via `os.getenv` **avec défauts `bge-m3`/`1024` codés en dur**, et **ne fait aucun `load_dotenv`** lui-même. | Le module marche même sans fichier d'env chargé. | Le `.env` n'influe sur les embeddings que si la variable est déjà présente dans le process (chargée par `retriever.py`/`generator.py`). Voir §6 bis. |

---

## 6. Base de données

| Sujet | Décision | Justification | Incertitude / à revoir |
|---|---|---|---|
| Moteur | **PostgreSQL + pgvector** (pas de vector DB séparée). | Tout le projet déjà aligné dessus ; suffisant pour le volume (~500 vecteurs). | — |
| Dimension vecteur | Schéma passé de `vector(384)` à **`vector(1024)`** pour BGE-M3. | Fait tant que la table était vide → indolore (sinon réencodage nécessaire). | `schema.sql` reflète bien `vector(1024)`. Le système tourne effectivement en 1024 (confirmé : « Void » répond correctement, y compris après que le `.env` soit réellement chargé). Voir §6 bis pour le chargement de la config. |
| `raw_content` | JSON brut **entier** du scraping. | Rôle du champ : garder la source intacte ; permet de tout reconstruire. | — |
| `token_count` | Estimation `caractères // 4`. | Champ non critique ; vrai comptage non nécessaire pour l'instant. | Approximatif ; nom de colonne un peu trompeur. |
| Doublons | **Ignorer** (`ON CONFLICT (source_url) DO NOTHING`). | Script rejouable sans casse ni doublon ; sûr pour l'apprentissage. | Mode « remplacer » à ajouter si re-scraping un jour. |
| Atomicité | 1 transaction par champion (document + chunks + embeddings). | Jamais d'état incohérent (document sans ses embeddings). En lot, un échec isolé n'annule pas les autres. | — |
| Insertion vecteur | Chaîne `"[...]"` castée `::vector` (pas d'adaptateur pgvector Python). | Garde le projet léger. | L'adaptateur `pgvector` serait plus « propre » ; changement mineur si voulu. |
| Index vectoriel | **Supprimé pour l'instant** (IVFFlat `lists=100` retiré). | Mal calibré pour ~500 vecteurs (IVFFlat visait ~100k) ; scan séquentiel = plus précis et assez rapide à cette échelle. | Réintroduire un index **calibré** quand le corpus grossira (stories). |

---

## 6 bis. Chargement de la configuration (`.env`)

| Sujet | Décision / constat | Justification | Incertitude / à revoir |
|---|---|---|---|
| Bug d'origine | Le code appelait `load_dotenv("_env")` (nom **sans point**). | Erreur héritée : lors d'un échange précédent, le `.env` déposé est apparu sous le nom `_env` (point initial mangé à l'upload), et ce nom erroné a été écrit tel quel dans le code. | — |
| Conséquence avant correctif | `load_dotenv("_env")` ne trouvait aucun fichier → **rien n'était chargé** ; tout tournait sur les défauts codés en dur (`bge-m3`/1024, URL Postgres, `llama3.1:8b`). | Explique pourquoi le projet « marchait » alors que le `.env` réel était ignoré. | — |
| Correctif | `load_dotenv("_env")` → **`load_dotenv()`** (sans argument) dans `retriever.py` et `generator.py`. | Recherche automatique du `.env` en remontant depuis le répertoire courant. | `load_dotenv()` part du *cwd*, pas du fichier `.py` : OK tant qu'on lance depuis la racine. Lancement depuis un sous-dossier → chemin à préciser. |
| Vérification | Valeur piège `OLLAMA_MODEL=modele-bidon-test` → Ollama renvoie `404` (modèle inexistant) en lancement direct. | Prouve que le `.env` est désormais lu (avant, la ligne aurait été ignorée). | **Confirmé en lancement direct uniquement.** Côté API (uvicorn), même *cwd* donc probablement OK, mais **pas encore vérifié** par le même test. |
| Contenu réel du `.env` | Non inspecté ligne à ligne. | — | Le fait que « Void » fonctionne **après** chargement du `.env` indique que le `.env` réel ne force PAS `EMBEDDING_MODEL=all-MiniLM`/384 (sinon les embeddings casseraient maintenant). La copie projet montrant ces valeurs est donc vraisemblablement obsolète. **Inférence à partir du résultat, à confirmer en ouvrant le vrai `.env`.** |

---

## 7. API HTTP (FastAPI)

| Sujet | Décision | Justification | Incertitude / à revoir |
|---|---|---|---|
| Exposition du RAG | API FastAPI dans `src/knowthelore/api/main.py` : `GET /health`, `POST /ask`. | Découpler le moteur de l'interface ; c'est l'API qui tournera sur le VPS. | — |
| `/ask` — entrée/sortie | Entrée `{question, k=5}` (modèle Pydantic) ; sortie = le dict de `answer()` tel quel (`answer`, `sources`, `chunks_used`, `no_context`). | Ne pas réécrire de couche de transformation inutile. | Sources = titres seulement (pas d'URL/score) ; enrichissement reporté au besoin du front. |
| Endpoint synchrone (`def`) | `/ask` en `def`, pas `async def`. | `answer()` est bloquant (Ollama jusqu'à 120 s) ; FastAPI exécute un `def` dans un threadpool, sans bloquer l'event loop. | — |
| Gestion d'erreur | `RuntimeError` → HTTP 503 (documenté dans Swagger). | Ollama injoignable/en erreur = service aval indisponible, pas un bug API. `EmbeddingError` hérite de `RuntimeError`, donc couvert. | Seul `503` traité explicitement ; autres codes via défauts FastAPI (`422` Pydantic sur corps invalide). |
| Branches testées | Dans le lore (OK) ; hors-lore → refus du LLM avec `no_context: false` et sources non vides (OK) ; Ollama coupé → 503 (OK) ; Ollama 500 transitoire → 503 (OK) ; JSON invalide → 422 (OK). | Confronter chaque branche au réel, pas seulement le cas heureux. | `retrieve()` n'a **pas** de seuil de similarité → ramène toujours k chunks ; le refus hors-lore vient donc du **prompt**, pas de `no_context`. Validation large reportée aux tests approfondis. |
| Packaging | Package installé en editable (`[tool.poetry] packages=[{include="knowthelore", from="src"}]`) ; `sys.path.insert` retirés de `retriever.py`/`generator.py`. | Imports `knowthelore.*` résolus proprement, sans béquille (vérifié en lancement direct ET via uvicorn). | Si déploiement VPS sans `poetry install` (copie de fichiers nue), les imports casseront → prévoir un vrai install du package. |

---

## 8. Déploiement (anticipé, non commencé)

| Sujet | Décision | Justification | Incertitude / à revoir |
|---|---|---|---|
| Cible | VPS envisagé. | — | VPS non choisi ; specs inconnues. Conseil à donner après mesure de la conso réelle, et avec recherche des offres à jour. |
| Docker | **Pas maintenant.** Conteneuriser éventuellement au déploiement. | Ajouterait une courbe d'apprentissage et de la friction en dev ; n'améliore pas le RAG. | Certains hébergeurs imposent Docker — à vérifier selon le VPS. |
| Code « docker-friendly » | Configuration par variables d'environnement (via `.env`, désormais réellement chargé — voir §6 bis). | Faciliter une conteneurisation future sans la faire tout de suite. | `embedder.py` reste sur défauts en dur (ne lit pas le `.env` lui-même) — à uniformiser avant déploiement si besoin. |

---

## 9. Stack technique (état constaté)

- **Python 3.12 + Poetry**
- **PostgreSQL 18.1** + **pgvector 0.8.1** (connexion et schéma validés)
- **Ollama** : `llama3.1:8b` (LLM, cold start ~20 s à gérer côté code), `bge-m3` (embeddings)
- **`fastapi` + `uvicorn` : installés**, utilisés par l'API.
- Adaptateur `pgvector` : optionnel, non installé (insertion vecteur par chaîne castée).
- Doublon `psycopg` (v3) + `psycopg2-binary` dans `pyproject.toml` : à trancher.

---

## 10. Points ouverts / dette assumée

- `.env` désormais réellement chargé (`load_dotenv()` au lieu du `"_env"` erroné) — **vérifié en lancement direct, à confirmer côté API (uvicorn)**. Contenu réel du `.env` à inspecter pour s'assurer qu'il ne porte pas d'anciennes valeurs (`all-MiniLM`/384) ; les indices disponibles suggèrent que non.
- `source_url` Universe : format à confirmer en navigateur.
- Taille de chunk et overlap : à recalibrer après mesure du retrieval.
- Recouvrement « propre » (par phrases) : raffinement reporté.
- Index vectoriel : à réintroduire, calibré, quand le volume grossira.
- Stories Universe : non encore scrapées/ingérées.
- Transcriptions YouTube : à réintégrer avec nettoyage des noms propres.
- Découpage en phrases (regex `.!?`) : grossier, peut se tromper sur « M. Yi », « 3.5 ».
- Sources de l'API limitées aux titres : enrichir (URL, score, officiel/canon) si le front en a besoin.
- Conformité Riot : à confirmer auprès d'eux.

---

*Aucune affirmation de ce document ne garantit l'absence d'erreurs résiduelles. Les choix marqués « incertitude » sont des hypothèses de travail à valider par la mesure ou l'expérience.*