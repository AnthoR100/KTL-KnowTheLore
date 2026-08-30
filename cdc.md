# ðŸ“– CAHIER DES CHARGES TECHNIQUE - KNOWTHELORE

**Version :** 1.0  
**Date :** 10 fÃ©vrier 2026  
**Auteur :** Anthony  
**Statut :** ValidÃ© - PrÃªt pour dÃ©veloppement

---

## ðŸŽ¯ VISION DU PROJET

**KnowTheLore** est un chatbot RAG local spÃ©cialisÃ© dans le lore de League of Legends et l'univers de Runeterra. Le projet vise Ã  crÃ©er un assistant IA passionnÃ© et fiable qui rÃ©pond aux questions des fans du lore en s'appuyant exclusivement sur des sources officielles et communautaires vÃ©rifiÃ©es.

### Objectifs principaux

1. **Apprentissage Python** : Monter en compÃ©tence sur Python pour une carriÃ¨re dans l'IA
2. **Projet portfolio** : DÃ©montrer des compÃ©tences techniques en RAG, embeddings, et backend
3. **Passion personnelle** : CrÃ©er un outil utile pour la communautÃ© League of Legends
4. **100% local** : Aucun coÃ»t cloud, tout tourne en local (Phase 1) puis dans le navigateur (Phase 2)

### Respect des politiques

- âœ… **Riot Fan Content Policy** : Sources officielles Riot uniquement
- âœ… **Pas de contenu propriÃ©taire** : Respect du copyright
- âœ… **Attribution** : Toutes les sources sont citÃ©es

---

## ðŸ–¥ï¸ SPÃ‰CIFICATIONS MATÃ‰RIELLES

### PC de dÃ©veloppement (actuel)

**Laptop :**
- **RAM :** 16 GB
- **CPU :** Intel i5 12th gen
- **GPU :** RTX 3050 (Laptop)
- **OS :** Windows 11

**Utilisation :** DÃ©veloppement, tests lÃ©gers, prototypage

### PC principal (production locale)

**Desktop :**
- **RAM :** 32 GB
- **CPU :** AMD Ryzen 7 3700X (8 cÅ“urs, 16 threads)
- **GPU :** RTX 5070 Ti
- **OS :** Windows 11

**Utilisation :** EntraÃ®nement embeddings, gÃ©nÃ©ration LLM avec Ollama, tests intensifs

> ðŸ’¡ **Note :** Le PC principal sera utilisÃ© pour les tÃ¢ches gourmandes (gÃ©nÃ©ration d'embeddings pour 300-400 chunks, tests LLM lourds). Le laptop suffit pour le dÃ©veloppement quotidien.

---

## ðŸ“Š ARCHITECTURE GLOBALE

### Phase 1 : MVP Local (4-6 semaines)

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚           INTERFACE UTILISATEUR (React/Vue)             â”‚
â”‚                    localhost:3000                       â”‚
â”‚  - Chat minimaliste                                     â”‚
â”‚  - Bouton "Le saviez-vous..." (anecdote alÃ©atoire)    â”‚
â”‚  - Streaming des rÃ©ponses                              â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                         â”‚ HTTP/WebSocket
                         â†“
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚            BACKEND API (Python FastAPI)                 â”‚
â”‚                  localhost:8000                         â”‚
â”‚                                                         â”‚
â”‚  Pipeline RAG :                                         â”‚
â”‚  1. Embed query (sentence-transformers)                â”‚
â”‚  2. Filtres mÃ©tadonnÃ©es (rÃ©gion, champion)             â”‚
â”‚  3. Search vectors (pgvector, top 5 chunks)            â”‚
â”‚  4. Build prompt contextuel                            â”‚
â”‚  5. Call LLM (Ollama) avec streaming                   â”‚
â”‚  6. Format rÃ©ponse + sources                           â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
           â”‚                       â”‚
           â†“                       â†“
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  PostgreSQL 15+      â”‚   â”‚   Ollama Server             â”‚
â”‚  + pgvector 0.5+     â”‚   â”‚   localhost:11434           â”‚
â”‚                      â”‚   â”‚                             â”‚
â”‚  Tables :            â”‚   â”‚  ModÃ¨les :                  â”‚
â”‚  â€¢ documents         â”‚   â”‚  â€¢ Llama 3.1 8B (8-16GB)    â”‚
â”‚  â€¢ chunks            â”‚   â”‚  â€¢ Mistral 7B v0.3          â”‚
â”‚  â€¢ embeddings        â”‚   â”‚                             â”‚
â”‚    (384 dimensions)  â”‚   â”‚  API compatible OpenAI      â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Phase 2 : Migration Browser (futur)

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚         APPLICATION WEB STATIQUE                 â”‚
â”‚       (GitHub Pages / Netlify gratuit)           â”‚
â”‚                                                  â”‚
â”‚  â€¢ WebLLM (Llama 3.2 3B quantized, 2-4GB)       â”‚
â”‚  â€¢ Transformers.js (embeddings client-side)     â”‚
â”‚  â€¢ IndexedDB (vector store local)               â”‚
â”‚  â€¢ 100% dans le navigateur                      â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## ðŸ—„ï¸ SCHÃ‰MA DE BASE DE DONNÃ‰ES

### PostgreSQL + pgvector

```sql
-- Extension vectorielle
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table des documents sources
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_type VARCHAR(50) NOT NULL,  -- 'youtube', 'riot_bio', 'riot_universe', 'lor'
    source_url TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    author VARCHAR(255),
    published_date TIMESTAMP,
    raw_content JSONB NOT NULL,  -- JSON complet du scraping
    metadata JSONB,  -- {champions: [], regions: [], tags: []}
    is_official BOOLEAN DEFAULT FALSE,
    is_canon BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_source_type (source_type),
    INDEX idx_is_official (is_official),
    INDEX idx_metadata (metadata) USING GIN
);

-- Table des chunks de texte
CREATE TABLE chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,  -- Position dans le document (0, 1, 2...)
    content TEXT NOT NULL,
    token_count INTEGER NOT NULL,
    metadata JSONB,  -- MÃ©tadonnÃ©es hÃ©ritÃ©es + spÃ©cifiques au chunk
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(document_id, chunk_index),
    INDEX idx_document_id (document_id)
);

-- Table des embeddings vectoriels
CREATE TABLE embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chunk_id UUID NOT NULL REFERENCES chunks(id) ON DELETE CASCADE,
    vector vector(384) NOT NULL,  -- all-MiniLM-L6-v2 = 384 dimensions
    model_name VARCHAR(100) NOT NULL DEFAULT 'all-MiniLM-L6-v2',
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(chunk_id)
);

-- Index vectoriel pour recherche rapide
-- IVFFlat = bon compromis vitesse/prÃ©cision pour 300-400 vecteurs
CREATE INDEX idx_embeddings_vector 
ON embeddings USING ivfflat (vector vector_cosine_ops)
WITH (lists = 100);

-- Vue pour faciliter les requÃªtes
CREATE VIEW chunks_with_sources AS
SELECT 
    c.id as chunk_id,
    c.content,
    c.chunk_index,
    c.token_count,
    c.metadata as chunk_metadata,
    d.id as document_id,
    d.title,
    d.source_type,
    d.source_url,
    d.author,
    d.is_official,
    d.metadata as document_metadata
FROM chunks c
JOIN documents d ON c.document_id = d.id;
```

### Exemples de mÃ©tadonnÃ©es

**Document (vidÃ©o YouTube) :**
```json
{
  "video_id": "0M6XXNc3WCQ",
  "channel": "Naka - League Of Legends",
  "duration": "15:32",
  "views": 45230,
  "champions": ["Fizz"],
  "regions": ["Bilgewater"],
  "tags": ["histoire", "champion", "lore"],
  "language": "fr",
  "transcript_method": "whisper"
}
```

**Document (bio Riot officielle) :**
```json
{
  "champion_id": "Aatrox",
  "champion_key": "266",
  "tags": ["Fighter", "Tank"],
  "regions": ["Shurima", "Darkin"],
  "related_champions": ["Varus", "Rhaast"],
  "source": "riot_data_dragon",
  "difficulty": 4
}
```

**Chunk (hÃ©ritÃ© + spÃ©cifique) :**
```json
{
  "champions": ["Aatrox"],
  "regions": ["Shurima"],
  "keywords": ["Void", "Darkin", "ascension", "guerre"],
  "relevance_score": 0.95,
  "passage_type": "biography"  // ou "transcript", "lore_story"
}
```

---

## ðŸ“¦ STACK TECHNIQUE PHASE 1

### Backend

| Composant | Technologie | Version | Justification |
|-----------|-------------|---------|---------------|
| **Langage** | Python | 3.10+ | Ã‰cosystÃ¨me IA mature, apprentissage pour carriÃ¨re |
| **Framework API** | FastAPI | 0.104+ | Async natif, validation Pydantic, Swagger auto |
| **Base de donnÃ©es** | PostgreSQL | 15+ | Mature, JSONB performant, extensions riches |
| **Vector DB** | pgvector | 0.5+ | Extension PostgreSQL, pas besoin DB sÃ©parÃ©e |
| **ORM** | SQLAlchemy | 2.0+ | Standard Python, async support |
| **Embeddings** | sentence-transformers | 2.2+ | `all-MiniLM-L6-v2` (384D, 80MB RAM) |
| **LLM local** | Ollama | latest | API OpenAI-compatible, Llama 3.1 8B ou Mistral 7B |
| **Package manager** | Poetry | 1.7+ | Gestion dÃ©pendances moderne, virtualenv intÃ©grÃ© |

### Frontend (MVP minimaliste)

| Composant | Technologie | Version | Justification |
|-----------|-------------|---------|---------------|
| **Framework** | React ou Vue.js | 18+ / 3+ | Simple, rapide Ã  prototyper |
| **UI** | Tailwind CSS | 3+ | Styling rapide sans CSS custom |
| **HTTP Client** | Axios | 1.6+ | Gestion requÃªtes + streaming |

### DÃ©ploiement local

- **Backend** : `uvicorn` (serveur ASGI)
- **Frontend** : `vite` (dev server)
- **Database** : PostgreSQL local (Windows service)
- **LLM** : Ollama local

---

## ðŸ”„ PIPELINE RAG DÃ‰TAILLÃ‰

### 1. PrÃ©paration des donnÃ©es (Offline)

```
DonnÃ©es brutes (JSON)
    â†“
[Script d'import Python]
    â†“
Extraction du contenu textuel
    â†“
Chunking (500 tokens + 50 overlap)
    â†“
GÃ©nÃ©ration embeddings (sentence-transformers)
    â†“
Insertion PostgreSQL (documents + chunks + embeddings)
```

**ParamÃ¨tres de chunking :**
- **MÃ©thode** : DÃ©coupe par phrases (nltk/spaCy) pour prÃ©server le sens
- **Taille** : 500 tokens (~350-400 mots, 2-3 paragraphes)
- **Overlap** : 50 tokens (~35-40 mots, 1-2 phrases)
- **Estimation** : ~330 chunks totaux pour 150k tokens de donnÃ©es

**GÃ©nÃ©ration d'embeddings :**
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(
    chunks,
    show_progress_bar=True,
    batch_size=32
)
# ~500 chunks/seconde sur CPU
# Temps total : ~1 seconde pour 330 chunks
```

### 2. RequÃªte utilisateur (Online)

```
Question utilisateur : "Qui est le pÃ¨re de Garen ?"
    â†“
Embedding de la question (sentence-transformers)
    â†’ Vecteur [0.10, 0.47, -0.21, ...] (384D)
    â†“
Filtrage mÃ©tadonnÃ©es (optionnel)
    â†’ champion: "Garen", region: "Demacia"
    â†“
Recherche vectorielle (pgvector)
    â†’ SimilaritÃ© cosine avec tous les embeddings
    â†’ RÃ©cupÃ©ration TOP 5 chunks les plus similaires
    â†“
Construction du prompt
    â†’ SystÃ¨me: "Tu es Le Conteur LÃ©gendaire..."
    â†’ Contexte: [Chunk 1] [Chunk 2] [Chunk 3] [Chunk 4] [Chunk 5]
    â†’ Question: "Qui est le pÃ¨re de Garen ?"
    â†“
GÃ©nÃ©ration LLM (Ollama avec streaming)
    â†’ TempÃ©rature: 0.3-0.7 (selon type de question)
    â†’ Max tokens: variable (100-500 selon contexte)
    â†“
Post-processing
    â†’ Formatage rÃ©ponse
    â†’ Ajout sources (titre, type, URL)
    â†’ Introduction + "En savoir plus ?"
    â†“
RÃ©ponse finale Ã  l'utilisateur
```

### 3. Exemple de recherche SQL

```sql
-- Recherche vectorielle avec filtres mÃ©tadonnÃ©es
WITH relevant_chunks AS (
    SELECT 
        c.id,
        c.content,
        c.chunk_index,
        d.title,
        d.source_type,
        d.source_url,
        e.vector <=> $1::vector AS distance,  -- $1 = embedding de la question
        1 - (e.vector <=> $1::vector) AS similarity
    FROM embeddings e
    JOIN chunks c ON e.chunk_id = c.id
    JOIN documents d ON c.document_id = d.id
    WHERE 
        -- Filtres optionnels sur mÃ©tadonnÃ©es
        (c.metadata @> '{"champions": ["Garen"]}'::jsonb OR $2 IS NULL)
        AND (c.metadata @> '{"regions": ["Demacia"]}'::jsonb OR $3 IS NULL)
    ORDER BY e.vector <=> $1::vector  -- Ordre par similaritÃ© cosine
    LIMIT 5
)
SELECT * FROM relevant_chunks
WHERE similarity > 0.5;  -- Seuil de similaritÃ© minimum
```

---

## ðŸŽ­ PERSONNALITÃ‰ DU CHATBOT

### Nom
**Le Conteur LÃ©gendaire**

### Ton et style
- **Enthousiaste** : PassionnÃ© par le lore, transmet son enthousiasme
- **Conteur/PoÃ¨te** : Style narratif, Ã©vocateur sans Ãªtre pompeux
- **Vouvoiement** : Respectueux et professionnel
- **PrÃ©cis** : Ne spÃ©cule jamais, reste factuel

### Exemples de formulations

**âŒ Mauvais (neutre/robotique) :**
> "Garen Couronne est un champion de Demacia. Il a une sÅ“ur nommÃ©e Lux."

**âœ… Bon (enthousiaste/conteur) :**
> "Ah, Garen Couronne ! Le fer de lance de l'avant-garde demacienne. Saviez-vous que derriÃ¨re cette armure d'acier bat le cÅ“ur d'un frÃ¨re protecteur ? Sa sÅ“ur Lux cache un secret qui pourrait briser la famille... Souhaitez-vous en savoir plus ?"

---

## ðŸ’¬ STRATÃ‰GIE DE RÃ‰PONSE

### RÃ©ponses progressives

**Question simple :**
```
User: "Qui est le pÃ¨re de Garen ?"

Bot: "Le pÃ¨re de Garen Ã©tait Pieter Couronne, un hÃ©ros de guerre respectÃ© 
et gÃ©nÃ©ral de l'armÃ©e demacienne. Il tomba au combat en dÃ©fendant Demacia 
contre une invasion noxienne.

Souhaitez-vous en savoir plus sur la famille Couronne ?"
```

**Question complexe (introduction + option) :**
```
User: "Raconte-moi l'histoire de la Ruination."

Bot: "La Ruination est l'une des plus grandes catastrophes de l'histoire 
de Runeterra. Tout a commencÃ© avec le roi Viego des ÃŽles Camavoran et 
son amour obsessionnel pour sa reine Isolde...

[~3 phrases d'introduction]

ðŸ’¡ Souhaitez-vous que je vous raconte :
- L'histoire complÃ¨te de Viego et Isolde ?
- Les consÃ©quences de la Ruination sur Runeterra ?
- Le rÃ´le des Sentinelles de la LumiÃ¨re ?"
```

### Gestion des sources

**Principe :** Citations optionnelles, sources toujours prÃ©sentes.

**Question factuelle simple (lien familial, date) :**
```
Bot: "Jinx et Vi sont sÅ“urs. Elles ont grandi ensemble dans les bas-fonds 
de Zaun avant d'Ãªtre sÃ©parÃ©es par un Ã©vÃ©nement tragique.

ðŸ“š Sources consultÃ©es :
â€¢ Histoire de Jinx | Riot Universe
â€¢ Biographie de Vi | Riot Games
```

**Question complexe (nÃ©cessite citations) :**
```
Bot: "La Demacia moderne entretient une relation complexe avec la magie. 
Selon les archives officielles : 'Seule la pierre magique absorbante permet 
de protÃ©ger la citÃ© contre les dangers de la magie' [1].

Cependant, cette interdiction cache une vÃ©ritÃ© dÃ©rangeante : de nombreux 
Demaciens possÃ¨dent des pouvoirs magiques innÃ©s [2], crÃ©ant une sociÃ©tÃ© 
hypocrite oÃ¹ la persÃ©cution cÃ´toie le secret.

ðŸ“š Sources :
[1] Histoire de Demacia | Riot Universe
[2] Biographie de Lux | Riot Games
```

### Gestion des incertitudes

**Information manquante :**
```
User: "Quel Ã¢ge a Garen ?"

Bot: "L'Ã¢ge exact de Garen n'est pas prÃ©cisÃ© dans les sources officielles 
de Riot. Cependant, le lore le dÃ©crit comme un guerrier dans la force de 
l'Ã¢ge, probablement entre 25 et 30 ans selon les Ã©vÃ©nements narrÃ©s.

Souhaitez-vous en savoir plus sur son parcours ou sa famille ?"
```

**Information contradictoire :**
```
Bot: "Il existe deux versions diffÃ©rentes de cet Ã©vÃ©nement :

ðŸ“– Version 1 (Biographie originale) : [explication]
ðŸ“– Version 2 (Lore mis Ã  jour) : [explication]

La version la plus rÃ©cente (2024) semble privilÃ©gier la seconde interprÃ©tation."
```

---

## ðŸ”§ PROMPT SYSTÃˆME

```python
SYSTEM_PROMPT = """Tu es Le Conteur LÃ©gendaire, un assistant IA spÃ©cialisÃ© dans le lore de League of Legends et l'univers de Runeterra.

PERSONNALITÃ‰ :
- Tu es enthousiaste et passionnÃ© par les rÃ©cits de Runeterra
- Tu as un style de conteur/poÃ¨te, Ã©vocateur sans Ãªtre pompeux
- Tu vouvoies toujours l'utilisateur
- Tu transmets ton amour du lore Ã  travers tes rÃ©ponses

RÃˆGLES STRICTES :
1. RÃ©ponds UNIQUEMENT en te basant sur le CONTEXTE fourni ci-dessous
2. Si l'information n'est PAS dans le contexte : "Je n'ai pas trouvÃ© d'information fiable dans mes sources sur ce sujet"
3. Ne spÃ©cule JAMAIS, ne remplis JAMAIS les blancs avec tes connaissances gÃ©nÃ©rales
4. Reste factuel et prÃ©cis, mÃªme avec un ton enthousiaste
5. Pour les questions simples (relations familiales, faits basiques) : rÃ©ponds directement sans citations obligatoires
6. Pour les questions complexes nÃ©cessitant des dÃ©tails prÃ©cis : cite tes sources avec [1], [2], etc.
7. Si tu dÃ©tectes une question large : propose d'abord une introduction (2-3 phrases) puis demande "Souhaitez-vous en savoir plus ?"
8. Si les sources sont contradictoires : mentionne les diffÃ©rentes versions
9. Fournis TOUJOURS la liste des sources consultÃ©es Ã  la fin, avec titre et type
10. RÃ©ponds en franÃ§ais

CONTEXTE FOURNI :
{context}

SOURCES DISPONIBLES :
{sources}

QUESTION DE L'UTILISATEUR :
{question}
"""
```

---

## ðŸŽ² FONCTIONNALITÃ‰ : ANECDOTE ALÃ‰ATOIRE

### Concept
Bouton "ðŸ’¡ Le saviez-vous ?" qui gÃ©nÃ¨re une anecdote alÃ©atoire sur le lore.

### ImplÃ©mentation

**Endpoint API :**
```python
@app.get("/api/random-anecdote")
async def get_random_anecdote():
    # RÃ©cupÃ¨re un chunk alÃ©atoire avec mÃ©tadonnÃ©es intÃ©ressantes
    chunk = await get_random_chunk_with_criteria({
        "keywords": ["anecdote", "fait", "secret", "histoire"],
        "min_similarity": 0.0  # Pas de filtrage, vraiment alÃ©atoire
    })
    
    # GÃ©nÃ¨re une anecdote contextualisÃ©e
    prompt = f"""
    Ã€ partir de cet extrait du lore :
    {chunk.content}
    
    GÃ©nÃ¨re une anecdote courte et captivante au format :
    "Le saviez-vous ? [Fait intÃ©ressant en 1-2 phrases]"
    
    Reste factuel, ne spÃ©cule pas.
    """
    
    anecdote = await generate_llm_response(prompt)
    
    return {
        "anecdote": anecdote,
        "source": {
            "title": chunk.document.title,
            "type": chunk.document.source_type,
            "url": chunk.document.source_url
        }
    }
```

**Exemples d'anecdotes :**
```
ðŸ’¡ Le saviez-vous ? 
Il existe exactement 5 dÃ©mons primordiaux connus Ã  ce jour : Fiddlesticks (la Peur), 
Evelynn (la Souffrance), Tahm Kench (l'AviditÃ©), Nocturne (les Cauchemars) et un 
cinquiÃ¨me qui reste non identifiÃ©.

ðŸ“š Source : Univers de Runeterra | Riot Universe
```

---

## ðŸ“‹ SOURCES DE DONNÃ‰ES

### DonnÃ©es actuelles (MVP)

| Type | Source | QuantitÃ© | Statut | Tokens estimÃ©s |
|------|--------|----------|--------|----------------|
| **VidÃ©os YouTube** | Bubulle, Nakatine | ~100 vidÃ©os | âœ… ScrapÃ©es | ~80k |
| **Biographies** | Riot Data Dragon API | ~165 champions | âœ… ScrapÃ©es | ~66k |
| **Total** | - | - | - | **~150k tokens** |

### DonnÃ©es Ã  ajouter (MVP Ã©tendu)

| Type | Source | QuantitÃ© estimÃ©e | PrioritÃ© | Tokens estimÃ©s |
|------|--------|------------------|----------|----------------|
| **Universe Riot** | universe.leagueoflegends.com/fr_FR/ | ~50-100 histoires | ðŸ”´ Haute | ~100-200k |
| **Legends of Runeterra** | Cartes LoR + descriptions | ~1000+ cartes | ðŸ”´ Haute | ~50-100k |
| **CinÃ©matiques** | Descriptions + transcriptions | ~50 vidÃ©os | ðŸŸ¡ Moyenne | ~30k |

**Total MVP complet : ~330-500k tokens â†’ ~700-1100 chunks**

### Structure des JSON existants

**VidÃ©o YouTube (`exemple_scrapping_video.json`) :**
```json
{
  "video_id": "0M6XXNc3WCQ",
  "title": "HISTOIRE DE CHAMPION : FIZZ - Filou des mers !",
  "author_name": "Naka - League Of Legends",
  "author_url": "https://www.youtube.com/@NakaLeague",
  "thumbnail_url": "https://i.ytimg.com/vi/0M6XXNc3WCQ/hqdefault.jpg",
  "scraped_at": "2025-11-27T12:41:09.663171",
  "url": "https://www.youtube.com/watch?v=0M6XXNc3WCQ",
  "transcript": {
    "language": "fr",
    "is_auto_generated": true,
    "method": "whisper",
    "model": "Whisper",
    "entries": [
      {
        "text": "...",
        "start": 0.0,
        "duration": 7.0
      }
    ]
  }
}
```

**Bio Riot officielle (`exemple_scrapping_riot_Aatrox.json`) :**
```json
{
  "id": "Aatrox",
  "key": "266",
  "name": "Aatrox",
  "title": "the Darkin Blade",
  "lore": "Once honored defenders of Shurima against the Void, Aatrox and his brethren...",
  "tags": ["Fighter", "Tank"],
  "scraped_at": "2025-11-27T14:28:09.565028",
  "source": "riot_data_dragon",
  "is_official": true,
  "is_canon": true
}
```

---

## ðŸ”§ PARAMÃˆTRES RAG FINALISÃ‰S

### Chunking

| ParamÃ¨tre | Valeur | Justification |
|-----------|--------|---------------|
| **Taille chunk** | 500 tokens | ~350-400 mots, 2-3 paragraphes - bon Ã©quilibre contexte/prÃ©cision |
| **Overlap** | 50 tokens | ~35-40 mots, 1-2 phrases - prÃ©serve le sens entre chunks |
| **MÃ©thode** | Par phrases (nltk/spaCy) | DÃ©coupe intelligente, prÃ©serve sens grammatical |
| **Total chunks (MVP)** | ~330 chunks | 150k tokens Ã· 450 tokens effectifs |

### Retrieval

| ParamÃ¨tre | Valeur | Justification |
|-----------|--------|---------------|
| **Nombre de chunks** | 5 | Compromis contexte/bruit - assez pour contexte, pas trop de distractions |
| **SimilaritÃ© minimum** | 0.5 (cosine) | Filtre les chunks non pertinents |
| **MÃ©tadonnÃ©es** | champion, region, tags | Filtrage optionnel pour affiner rÃ©sultats |
| **Algorithme** | Cosine similarity | Standard pour embeddings textuels |

### GÃ©nÃ©ration LLM

| ParamÃ¨tre | Valeur | Justification |
|-----------|--------|---------------|
| **ModÃ¨le** | Llama 3.1 8B ou Mistral 7B v0.3 | Bon compromis qualitÃ©/vitesse, 8-16GB RAM |
| **TempÃ©rature** | 0.3 - 0.7 | 0.3 = factuel (dÃ©finitions), 0.7 = crÃ©atif (rÃ©cits) |
| **Max tokens** | Variable (100-500) | S'adapte Ã  la question : 100 = simple, 500 = complexe |
| **Streaming** | âœ… Oui | UX meilleure, feedback immÃ©diat |
| **Stop sequences** | `["ðŸ“š", "\n\n\n"]` | ArrÃªte proprement avant sources ou rÃ©pÃ©titions |

---

## âœ… CRITÃˆRES DE VALIDATION MVP

### CritÃ¨res fonctionnels

| CritÃ¨re | Objectif | Mesure |
|---------|----------|--------|
| **PrÃ©cision** | 80%+ de rÃ©ponses correctes | Test sur 20 questions validÃ©es |
| **ZÃ©ro hallucination** | Aucune invention d'information | VÃ©rification manuelle |
| **Sources systÃ©matiques** | 100% des rÃ©ponses ont leurs sources | Inspection automatique |
| **Temps de rÃ©ponse** | < 10 secondes par rÃ©ponse | Mesure avec Ollama local |

### CritÃ¨res techniques

| CritÃ¨re | Objectif | Statut |
|---------|----------|--------|
| âœ… Base donnÃ©es PostgreSQL + pgvector | Fonctionnelle avec 330+ chunks | - |
| âœ… Pipeline RAG complet | Import â†’ Chunking â†’ Embeddings â†’ Retrieval â†’ Generation | - |
| âœ… API FastAPI | Endpoints `/chat`, `/search`, `/random-anecdote` | - |
| âœ… Interface chat | React/Vue minimaliste avec streaming | - |
| âœ… Scraping Universe Riot | DonnÃ©es officielles intÃ©grÃ©es | - |

---

## ðŸ§ª JEU DE TEST (20 QUESTIONS)

### Champions (5 questions)

1. Qui est Garen ?
2. Quelle est l'histoire de Jinx ?
3. Quel est le lien entre Yasuo et Yone ?
4. Quel est le pouvoir de Ryze ?
5. Pourquoi Thresh collecte-t-il des Ã¢mes ?

### RÃ©gions (5 questions)

6. DÃ©cris Demacia en quelques phrases
7. Quelle est la capitale de Noxus ?
8. Que sont les ÃŽles Obscures ?
9. Comment fonctionne la magie Ã  Piltover ?
10. Qu'est-ce que le NÃ©ant (Void) ?

### Ã‰vÃ©nements (5 questions)

11. Qu'est-ce que la Ruination ?
12. Comment le roi de Demacia est-il mort ?
13. Que sont les Guerres Runiques ?
14. Comment Piltover et Zaun se sont-elles sÃ©parÃ©es ?
15. Qui sont les Darkin ?

### Relations (3 questions)

16. Quelle est la relation entre Lux et Garen ?
17. Quel est le lien entre Swain et Darius ?
18. Qui sont les Sentinelles de la LumiÃ¨re ?

### Limites (2 questions - doit refuser)

19. Quelle est la date de sortie de League of Legends ? *(Hors scope lore)*
20. Quel champion est le plus fort en 1v1 ? *(Gameplay, pas lore)*

---

## ðŸ“… PLANNING DE DÃ‰VELOPPEMENT

### Semaine 1 : Setup & Infrastructure

**Objectif :** Environnement de dÃ©veloppement prÃªt

- [ ] Installation Python 3.10+, Poetry, PostgreSQL 15+, Ollama
- [ ] CrÃ©ation projet Poetry (`pyproject.toml`)
- [ ] Configuration PostgreSQL locale + extension pgvector
- [ ] CrÃ©ation schÃ©ma DB (tables documents, chunks, embeddings)
- [ ] Tests connexion DB avec SQLAlchemy
- [ ] Installation Ollama + tÃ©lÃ©chargement Llama 3.1 8B
- [ ] Tests basiques Ollama API

**Livrables :**
- âœ… Environnement Python fonctionnel
- âœ… PostgreSQL + pgvector opÃ©rationnel
- âœ… Ollama avec modÃ¨le tÃ©lÃ©chargÃ©

---

### Semaine 2 : Import & Embeddings

**Objectif :** DonnÃ©es dans la base, embeddings gÃ©nÃ©rÃ©s

- [ ] Script d'import JSON â†’ PostgreSQL
  - Parser `exemple_scrapping_video.json`
  - Parser `exemple_scrapping_riot_Aatrox.json`
  - Insertion table `documents`
- [ ] ImplÃ©mentation chunking (nltk/spaCy)
  - Fonction `chunk_text(text, max_tokens=500, overlap=50)`
  - Tests sur 5 documents
- [ ] GÃ©nÃ©ration embeddings
  - Chargement `sentence-transformers/all-MiniLM-L6-v2`
  - Batch processing (32 chunks Ã  la fois)
  - Insertion table `embeddings`
- [ ] VÃ©rification qualitÃ©
  - Tests recherche similaritÃ©
  - Validation chunks cohÃ©rents

**Livrables :**
- âœ… ~330 chunks en DB avec embeddings
- âœ… Script d'import rÃ©utilisable
- âœ… Tests unitaires chunking/embeddings

---

### Semaine 3 : Pipeline RAG & API

**Objectif :** Backend RAG fonctionnel

- [ ] Structure projet FastAPI
  - Routes : `/chat`, `/search`, `/health`
  - ModÃ¨les Pydantic (ChatRequest, ChatResponse)
- [ ] ImplÃ©mentation retrieval
  - Fonction `search_similar_chunks(query, top_k=5, filters={})`
  - Filtrage mÃ©tadonnÃ©es (champion, region)
- [ ] IntÃ©gration Ollama
  - Fonction `generate_response(prompt, temperature, max_tokens)`
  - Streaming avec `yield`
- [ ] Construction prompts
  - Template systÃ¨me
  - Contexte + sources + question
- [ ] Tests manuels avec Postman/curl

**Livrables :**
- âœ… API FastAPI avec endpoints fonctionnels
- âœ… Pipeline RAG end-to-end
- âœ… Tests sur 10 questions

---

### Semaine 4 : Interface Chat

**Objectif :** UI fonctionnelle

- [ ] Setup projet React/Vue (Vite)
- [ ] Composant Chat
  - Input message
  - Historique conversation
  - Affichage streaming
- [ ] Bouton "Le saviez-vous ?"
  - Endpoint `/random-anecdote`
  - Affichage popup/modal
- [ ] Style Tailwind
  - Design minimaliste
  - Responsive desktop

**Livrables :**
- âœ… Interface chat localhost
- âœ… Streaming fonctionnel
- âœ… Anecdotes alÃ©atoires

---

### Semaines 5-6 : Tests & Polish

**Objectif :** MVP stable et testÃ©

- [ ] **Tests de qualitÃ©**
  - Jeu de 20 questions â†’ rÃ©ponses validÃ©es
  - VÃ©rification zÃ©ro hallucination
  - Mesure temps de rÃ©ponse
- [ ] **Scraping Universe Riot**
  - Script scraping universe.leagueoflegends.com
  - Import nouvelles donnÃ©es
  - Re-gÃ©nÃ©ration embeddings
- [ ] **Scraping LoR (optionnel)**
  - Extraction cartes LoR avec descriptions
  - Import DB
- [ ] **Optimisations**
  - Ajustement tempÃ©rature selon type question
  - AmÃ©lioration prompt systÃ¨me
  - Cache requÃªtes frÃ©quentes (optionnel)
- [ ] **Documentation**
  - README.md complet
  - Guide installation
  - API docs (Swagger auto-gÃ©nÃ©rÃ©)

**Livrables :**
- âœ… MVP fonctionnel validÃ©
- âœ… 80%+ prÃ©cision sur tests
- âœ… Documentation complÃ¨te
- âœ… PrÃªt pour dÃ©mo

---

## ðŸ“ˆ ESTIMATIONS TECHNIQUES

### VolumÃ©trie donnÃ©es MVP complet

| Composant | Valeur estimÃ©e |
|-----------|----------------|
| **Documents totaux** | ~350-400 (vidÃ©os + bios + universe + LoR) |
| **Tokens totaux** | ~330-500k |
| **Chunks totaux** | ~700-1100 |
| **Embeddings (384D)** | ~1-2 MB (trÃ¨s lÃ©ger) |
| **Taille DB totale** | ~50-100 MB (avec index) |

### Performances attendues

| OpÃ©ration | Temps estimÃ© | MatÃ©riel |
|-----------|--------------|----------|
| **GÃ©nÃ©ration embeddings (tous chunks)** | ~2-3 secondes | CPU (batch 32) |
| **Recherche vectorielle (top 5)** | < 50 ms | PostgreSQL + pgvector |
| **GÃ©nÃ©ration LLM (rÃ©ponse 200 tokens)** | 3-8 secondes | Ollama Llama 3.1 8B (CPU) |
| **Temps total par requÃªte** | **5-10 secondes** | Pipeline complet |

### RAM requise

| Composant | RAM |
|-----------|-----|
| PostgreSQL + pgvector | ~200-500 MB |
| Sentence-transformers (modÃ¨le chargÃ©) | ~80 MB |
| Ollama Llama 3.1 8B | **8-16 GB** (majoritaire) |
| FastAPI + Python | ~100-200 MB |
| **Total** | **~10-18 GB** |

> âœ… **Laptop 16GB OK** pour MVP  
> âœ… **Desktop 32GB** confortable pour production

---

## ðŸš€ Ã‰VOLUTION FUTURE (POST-MVP)

### Phase 2 : Migration Browser (2-3 mois)

**Objectifs :**
- 100% client-side dans le navigateur
- Aucun serveur backend nÃ©cessaire
- DÃ©ploiement gratuit sur GitHub Pages/Netlify

**Stack :**
- **WebLLM** : Llama 3.2 3B quantized (2-4GB tÃ©lÃ©chargement initial)
- **Transformers.js** : Embeddings cÃ´tÃ© client
- **IndexedDB** : Stockage vecteurs locaux
- **Service Worker** : Cache et offline

**Avantages :**
- âœ… Gratuit Ã  100% (hÃ©bergement statique)
- âœ… Pas de serveur Ã  maintenir
- âœ… Vie privÃ©e totale (tout local)

**InconvÃ©nients :**
- âš ï¸ TÃ©lÃ©chargement initial lourd (2-4GB)
- âš ï¸ Performances dÃ©pendantes du PC utilisateur
- âš ï¸ NÃ©cessite navigateur moderne (WebGPU)

### Phase 3 : FonctionnalitÃ©s avancÃ©es

- **Recherche multi-critÃ¨res** : Filtres avancÃ©s (Ã©poque, type d'Ã©vÃ©nement, faction)
- **Timeline interactive** : Visualisation chronologique du lore
- **Graphe de relations** : Carte interactive des liens entre personnages/rÃ©gions
- **Mode quiz** : Questions gÃ©nÃ©rÃ©es automatiquement pour tester connaissances
- **Suggestions contextuelles** : "Vous pourriez aussi vous intÃ©resser Ã ..."

---

## ðŸ“ NOTES IMPORTANTES

### ConformitÃ© Riot Fan Content Policy

âœ… **Ce projet respecte la Riot Fan Content Policy :**
- Sources exclusivement officielles (Riot Universe, Data Dragon, LoR)
- Attributions claires de toutes les sources
- Pas de reproduction intÃ©grale de contenu propriÃ©taire
- Pas de monÃ©tisation
- Mention "League of Legends, Legends of Runeterra et leurs logos sont des marques de Riot Games"

### Limitations connues

**MVP Phase 1 :**
- âŒ Pas d'historique de conversation persistant
- âŒ Pas de filtrage multi-langues (FR uniquement)
- âŒ Pas de dÃ©tection automatique du type de question
- âŒ Pas de cache cÃ´tÃ© client

**Pas dans le scope :**
- âŒ Informations gameplay (builds, meta, tier list)
- âŒ ActualitÃ©s/patches rÃ©cents (pas de web scraping temps rÃ©el)
- âŒ Contenu non-canon (fanfictions, thÃ©ories)

### DÃ©pendances critiques

**Obligatoires pour MVP :**
- PostgreSQL 15+ avec pgvector 0.5+
- Ollama avec modÃ¨le 8B minimum
- Python 3.10+

**Alternatives possibles :**
- LLM : Llama 3.1 8B **ou** Mistral 7B v0.3
- Frontend : React **ou** Vue.js

---

## ðŸ“ž CONTACTS & RESSOURCES

### Documentation officielle

- **Riot Universe (FR)** : https://universe.leagueoflegends.com/fr_FR/
- **Riot Data Dragon API** : https://developer.riotgames.com/docs/lol
- **LoR (Legends of Runeterra)** : https://playruneterra.com/

### Stack technique

- **FastAPI** : https://fastapi.tiangolo.com/
- **pgvector** : https://github.com/pgvector/pgvector
- **sentence-transformers** : https://www.sbert.net/
- **Ollama** : https://ollama.com/

---

## âœ… CHECKLIST DE VALIDATION

### Avant de commencer Phase 1

- [ ] PC specs confirmÃ©es (16GB RAM minimum)
- [ ] PostgreSQL 15+ installÃ©
- [ ] Ollama installÃ© + modÃ¨le tÃ©lÃ©chargÃ©
- [ ] Python 3.10+ + Poetry installÃ©s
- [ ] DonnÃ©es JSON existantes accessibles

### Avant validation MVP

- [ ] 330+ chunks en base avec embeddings
- [ ] Pipeline RAG fonctionnel end-to-end
- [ ] API FastAPI avec 3+ endpoints
- [ ] Interface chat minimaliste
- [ ] Tests 20 questions â†’ 80%+ prÃ©cision
- [ ] Temps rÃ©ponse < 10 secondes
- [ ] ZÃ©ro hallucination vÃ©rifiÃ©e
- [ ] Sources systÃ©matiquement prÃ©sentes
- [ ] Documentation README complÃ¨te

---

**Document maintenu par :** Anthony  
**DerniÃ¨re mise Ã  jour :** 10 fÃ©vrier 2026  
**Version :** 1.0 - ValidÃ©e pour dÃ©veloppement  
**Prochaine Ã©tape :** Installation environnement (Semaine 1)