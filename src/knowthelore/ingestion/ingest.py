"""
Insertion en base d'un ParsedDocument (champion OU région) : document + chunks + embeddings.
Décisions appliquées : raw_content entier, token_count ≈ car//4, doublons ignorés,
transaction atomique.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import psycopg
from psycopg.types.json import Json
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from knowthelore.ingestion.parser import (
    parse_universe_champion,
    parse_universe_region,
    ParsedDocument,
)
from knowthelore.ingestion.chunker import chunk_text
from knowthelore.embeddings.embedder import embed_batch

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL n'est pas défini (vérifie ton .env)")
MODEL_NAME = os.getenv("EMBEDDING_MODEL", "bge-m3")


def insert_parsed(doc: ParsedDocument, raw: dict, conn: psycopg.Connection) -> tuple[str, int]:
    """
    Insère un ParsedDocument déjà parsé + son JSON brut. Générique (champion ou région).
    Renvoie (statut, nb_chunks) : "inserted" | "skipped" | "no_content".
    """
    chunks = chunk_text(doc.content)
    if not chunks:
        return ("no_content", 0)

    doc_metadata = {**doc.metadata, "language": doc.language}

    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO documents
                    (source_type, source_url, title, author, published_date,
                     raw_content, metadata, is_official, is_canon)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (source_url) DO NOTHING
                RETURNING id;
                """,
                (
                    doc.source_type, doc.source_url, doc.title, None, None,
                    Json(raw), Json(doc_metadata), doc.is_official, doc.is_canon,
                ),
            )
            row = cur.fetchone()
            if row is None:
                return ("skipped", 0)
            document_id = row[0]

            vectors = embed_batch([c.text for c in chunks])
            if len(vectors) != len(chunks):
                raise RuntimeError(
                    f"{len(vectors)} vecteurs pour {len(chunks)} chunks : incohérent."
                )

            for c, vec in zip(chunks, vectors):
                cur.execute(
                    """
                    INSERT INTO chunks (document_id, chunk_index, content, token_count, metadata)
                    VALUES (%s, %s, %s, %s, %s) RETURNING id;
                    """,
                    (
                        document_id, c.index, c.text, c.char_count // 4,
                        Json({
                            "champions": doc.metadata.get("champions", []),
                            "regions": doc.metadata.get("regions", []),
                            "passage_type": doc.metadata.get("passage_type"),
                        }),
                    ),
                )
                chunk_id = cur.fetchone()[0]
                vec_str = "[" + ",".join(map(str, vec)) + "]"
                cur.execute(
                    "INSERT INTO embeddings (chunk_id, vector, model_name) "
                    "VALUES (%s, %s::vector, %s);",
                    (chunk_id, vec_str, MODEL_NAME),
                )

    return ("inserted", len(chunks))


def _ingest_with(parser_fn, path: str | Path, conn: psycopg.Connection) -> tuple[str, int]:
    """Parse un fichier avec parser_fn, lit le JSON brut, puis insère."""
    path = Path(path)
    doc = parser_fn(path)
    if doc is None:
        return ("no_content", 0)
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return insert_parsed(doc, raw, conn)


def ingest_champion(path: str | Path, conn: psycopg.Connection) -> tuple[str, int]:
    return _ingest_with(parse_universe_champion, path, conn)


def ingest_region(path: str | Path, conn: psycopg.Connection) -> tuple[str, int]:
    return _ingest_with(parse_universe_region, path, conn)


if __name__ == "__main__":
    test_path = sys.argv[1] if len(sys.argv) > 1 else "data/raw/universe_regions/ionia.json"
    conn = psycopg.connect(DATABASE_URL)
    try:
        statut, n = ingest_region(test_path, conn)
        print(f"Statut : {statut} | chunks insérés : {n}")
    finally:
        conn.close()