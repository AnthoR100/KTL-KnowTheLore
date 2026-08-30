"""
Retrieval pour KnowTheLore.

Rôle : pour une question en texte, retrouver les chunks de lore les plus proches
par similarité sémantique (BGE-M3 + pgvector, distance cosinus).
Testable seul, SANS le LLM : c'est ici que se jugent la plupart des problèmes d'un RAG.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass

import psycopg
from dotenv import load_dotenv

from knowthelore.embeddings.embedder import embed_text

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL n'est pas défini (vérifie ton .env)")


@dataclass
class RetrievedChunk:
    """Un chunk retrouvé, avec sa source et son score de proximité."""
    content: str
    title: str            # titre du document source (ex. "Ahri, Renard à neuf queues")
    source_url: str
    chunk_index: int
    is_official: bool
    is_canon: bool
    similarity: float     # 1.0 = identique, plus c'est haut, plus c'est proche
    metadata: dict


def retrieve(question: str, k: int = 5, conn: psycopg.Connection | None = None) -> list[RetrievedChunk]:
    """
    Renvoie les k chunks les plus proches de `question`, du plus proche au moins proche.
    """
    if not question or not question.strip():
        return []

    # 1. Encoder la question avec LE MÊME modèle que les chunks (BGE-M3)
    q_vector = embed_text(question)
    vec_str = "[" + ",".join(map(str, q_vector)) + "]"

    # 2. Recherche par distance cosinus (<=>). similarity = 1 - distance.
    sql = """
        SELECT
            c.content,
            d.title,
            d.source_url,
            c.chunk_index,
            d.is_official,
            d.is_canon,
            c.metadata,
            1 - (e.vector <=> %s::vector) AS similarity
        FROM embeddings e
        JOIN chunks c    ON e.chunk_id = c.id
        JOIN documents d ON c.document_id = d.id
        ORDER BY e.vector <=> %s::vector
        LIMIT %s;
    """

    own_conn = conn is None
    if own_conn:
        conn = psycopg.connect(DATABASE_URL)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (vec_str, vec_str, k))
            rows = cur.fetchall()
    finally:
        if own_conn:
            conn.close()

    return [
        RetrievedChunk(
            content=r[0],
            title=r[1],
            source_url=r[2],
            chunk_index=r[3],
            is_official=r[4],
            is_canon=r[5],
            metadata=r[6] or {},
            similarity=float(r[7]),
        )
        for r in rows
    ]


if __name__ == "__main__":
    # Test interactif : pose une question en argument, ou en boucle.
    if len(sys.argv) > 1:
        questions = [" ".join(sys.argv[1:])]
    else:
        questions = None  # mode boucle

    def montrer(question: str):
        print(f"\n❓ Question : {question}")
        print("=" * 60)
        results = retrieve(question, k=5)
        if not results:
            print("Aucun résultat.")
            return
        for i, r in enumerate(results, 1):
            print(f"\n[{i}] {r.title}  (chunk {r.chunk_index})")
            print(f"    similarité : {r.similarity:.4f}")
            champ = r.metadata.get("champions", [])
            region = r.metadata.get("regions", [])
            print(f"    champions : {champ} | régions : {region}")
            extrait = r.content[:200].replace("\n", " ")
            print(f"    extrait : {extrait}...")

    if questions:
        for q in questions:
            montrer(q)
    else:
        print("Mode interactif. Tape une question (ou 'q' pour quitter).")
        while True:
            try:
                q = input("\n> ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if q.lower() in {"q", "quit", "exit"}:
                break
            if q:
                montrer(q)