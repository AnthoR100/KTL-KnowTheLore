-- Extension vectorielle
CREATE EXTENSION IF NOT EXISTS vector;

-- Table des documents sources
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_type VARCHAR(50) NOT NULL,  -- 'youtube', 'riot_bio', 'riot_universe', 'lor', 'index'
    source_url TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    author VARCHAR(255),
    published_date TIMESTAMP,
    raw_content JSONB NOT NULL,  -- JSON complet du scraping
    metadata JSONB,  -- {champions: [], regions: [], tags: []}
    is_official BOOLEAN DEFAULT FALSE,
    is_canon BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index pour optimiser les recherches
CREATE INDEX idx_source_type ON documents(source_type);
CREATE INDEX idx_is_official ON documents(is_official);
CREATE INDEX idx_metadata ON documents USING GIN(metadata);

-- Table des chunks de texte
CREATE TABLE chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,  -- Position dans le document (0, 1, 2...)
    content TEXT NOT NULL,
    token_count INTEGER NOT NULL,
    metadata JSONB,  -- Métadonnées héritées + spécifiques au chunk
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(document_id, chunk_index)
);

CREATE INDEX idx_document_id ON chunks(document_id);

-- Table des embeddings vectoriels
CREATE TABLE embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chunk_id UUID NOT NULL REFERENCES chunks(id) ON DELETE CASCADE,
    vector vector(1024) NOT NULL,  -- bge-m3 = 1024 dimensions
    model_name VARCHAR(100) NOT NULL DEFAULT 'bge-m3',
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(chunk_id)
);

-- Pas d'index vectoriel pour l'instant : à ~500-600 vecteurs, le scan
-- séquentiel de pgvector est exact et déjà rapide (< 50ms). Un index
-- (IVFFlat ou HNSW), correctement calibré sur le volume réel, sera à
-- réintroduire quand le corpus grossira significativement (cf. DECISIONS.md).

-- Vue pour faciliter les requêtes
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