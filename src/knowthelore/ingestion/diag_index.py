"""
Diagnostic Option D — lecture seule.

Deux questions :
1. Les documents index (source_type='index') sont-ils bien en base ?
2. Sur les questions agrégées, à quel RANG (parmi tous les chunks) et à quelle
   similarité se classe le chunk index ? Le retriever normal ne montre que le
   top-5 ; ici on voit le rang exact même s'il est au-delà.

Placement suggéré : knowthelore/ingestion/diag_index.py
Lancement : poetry run python -m knowthelore.ingestion.diag_index
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import psycopg
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from knowthelore.embeddings.embedder import embed_text

_env_loaded = load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL n'est pas défini (vérifie ton .env)")

QUESTIONS = [
    "combien y a-t-il de régions dans Runeterra",
    "liste les régions de Runeterra",
    "combien de champions existe-t-il",
    "quels sont les champions de League of Legends",
]

# Pour la question donnée (vecteur), calcule le rang de CHAQUE chunk parmi tous,
# puis ne garde que les chunks des documents index.
PROBE_SQL = """
SELECT title, sim, rnk FROM (
    SELECT d.title,
           1 - (e.vector <=> %s::vector) AS sim,
           rank() OVER (ORDER BY e.vector <=> %s::vector) AS rnk,
           d.source_type
    FROM embeddings e
    JOIN chunks c    ON e.chunk_id = c.id
    JOIN documents d ON c.document_id = d.id
) t
WHERE source_type = 'index'
ORDER BY sim DESC;
"""


def main() -> None:
    print("_env trouvé   :", bool(_env_loaded))
    print("DATABASE_URL  :", re.sub(r"://([^:/@]+):[^@]*@", r"://\1:***@", DATABASE_URL))
    conn = psycopg.connect(DATABASE_URL)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT title FROM documents "
                "WHERE source_type = 'index' ORDER BY title;"
            )
            idx = [r[0] for r in cur.fetchall()]

        print("=" * 64)
        print(f"Documents index en base : {len(idx)}")
        for t in idx:
            print(f"   - {t}")
        if not idx:
            print(
                "\n⛔ Aucun document index trouvé. L'étape --write n'a rien inséré.\n"
                "   Relance d'abord :\n"
                "   poetry run python -m knowthelore.ingestion.build_index_chunk --write"
            )
            return

        for q in QUESTIONS:
            v = embed_text(q)
            vec_str = "[" + ",".join(map(str, v)) + "]"
            with conn.cursor() as cur:
                cur.execute(PROBE_SQL, (vec_str, vec_str))
                rows = cur.fetchall()
            print(f"\n❓ {q}")
            for title, sim, rnk in rows:
                etat = "✅ dans le top-5" if rnk <= 5 else "❌ hors top-5"
                print(f"   {title:48s} sim={sim:.4f}  rang={rnk}  {etat}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()