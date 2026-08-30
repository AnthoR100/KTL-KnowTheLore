"""
Débogage écriture index — pourquoi --write annonce un succès alors que
diag_index ne trouve rien.

Dans UN seul processus, on mesure :
  - _env trouvé ou non, et l'URL de base réellement utilisée (mot de passe masqué)
  - nb de docs index vus dans la MÊME session, juste après store_all
  - nb de docs index vus par une NOUVELLE connexion (= ce que verra diag_index)
  - la répartition de tous les source_type

Interprétation :
  - même=2 et nouvelle=2  -> les données persistent ; si diag_index voit 0,
    c'est que diag_index tape une autre base (comparer les URL affichées).
  - même=2 et nouvelle=0  -> problème de commit / persistance.
  - même=0                -> l'insert n'atterrit pas (malgré l'absence d'erreur).

Placement suggéré : knowthelore/ingestion/diag_write.py
Lancement : poetry run python -m knowthelore.ingestion.diag_write
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import psycopg
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from knowthelore.ingestion.build_index_chunk import (
    build_index_texts,
    store_all,
    DATABASE_URL,
)


def masked(url: str) -> str:
    """Masque le mot de passe dans une URL postgres."""
    return re.sub(r"://([^:/@]+):[^@]*@", r"://\1:***@", url)


def counts(conn: psycopg.Connection):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM documents WHERE source_type = 'index';")
        idx = cur.fetchone()[0]
        cur.execute(
            "SELECT source_type, count(*) FROM documents "
            "GROUP BY source_type ORDER BY 1;"
        )
        repartition = cur.fetchall()
    return idx, repartition


def main() -> None:
    print("_env trouvé   :", bool(load_dotenv("_env")))
    print("DATABASE_URL  :", masked(DATABASE_URL))

    conn = psycopg.connect(DATABASE_URL)
    try:
        data = build_index_texts(conn)
        if data["autres"]:
            print("Documents non classés présents — on s'arrête.")
            return
        store_all(conn, data)
        idx_same, _ = counts(conn)
        print(f"\nMême session après store_all : {idx_same} doc(s) index")
    finally:
        conn.close()

    check = psycopg.connect(DATABASE_URL)
    try:
        idx_fresh, repartition = counts(check)
        print(f"Nouvelle connexion           : {idx_fresh} doc(s) index")
        print("\nRépartition source_type (nouvelle connexion) :")
        for st, n in repartition:
            print(f"   {st!r:22s} : {n}")
    finally:
        check.close()


if __name__ == "__main__":
    main()