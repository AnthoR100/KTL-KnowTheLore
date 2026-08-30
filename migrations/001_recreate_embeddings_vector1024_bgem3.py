import os

import psycopg
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL n'est pas défini (vérifie ton .env)")

SQL = """
DROP INDEX IF EXISTS idx_embeddings_vector;
DROP TABLE IF EXISTS embeddings;

CREATE TABLE embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chunk_id UUID NOT NULL REFERENCES chunks(id) ON DELETE CASCADE,
    vector vector(1024) NOT NULL,
    model_name VARCHAR(100) NOT NULL DEFAULT 'bge-m3',
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(chunk_id)
);
"""

conn = psycopg.connect(DATABASE_URL)
with conn.cursor() as cur:
    cur.execute(SQL)
conn.commit()

# Vérification : on relit la dimension réelle de la colonne vector
with conn.cursor() as cur:
    cur.execute("""
        SELECT a.attname, format_type(a.atttypid, a.atttypmod)
        FROM pg_attribute a
        WHERE a.attrelid = 'embeddings'::regclass
          AND a.attname = 'vector';
    """)
    print("Colonne vector :", cur.fetchall())

conn.close()
print("Table embeddings recréée.")