"""
Ingestion du corpus complet : applique ingest_champion à toutes les fiches Universe.
Réutilise la fonction unitaire déjà validée. Chaque champion est inséré dans sa
propre transaction : un échec isolé n'annule pas les autres.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import psycopg
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from knowthelore.ingestion.ingest import ingest_champion

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL n'est pas défini (vérifie ton .env)")
INPUT_DIR = Path("data/raw/universe_champions")


def main():
    files = sorted(INPUT_DIR.glob("*.json"))
    if not files:
        print(f"Aucun fichier dans {INPUT_DIR}")
        return

    stats = {"inserted": 0, "skipped": 0, "no_content": 0, "error": 0}
    total_chunks = 0
    errors = []

    conn = psycopg.connect(DATABASE_URL)
    t0 = time.time()
    try:
        for idx, path in enumerate(files, 1):
            try:
                statut, n = ingest_champion(path, conn)
                stats[statut] += 1
                total_chunks += n
                print(f"[{idx}/{len(files)}] {path.stem:20s} -> {statut} ({n} chunks)")
            except Exception as e:
                # La transaction du champion a déjà été annulée (rollback).
                # On l'isole, on note, et on continue les suivants.
                stats["error"] += 1
                errors.append((path.stem, str(e)))
                print(f"[{idx}/{len(files)}] {path.stem:20s} -> ERREUR : {e}")
    finally:
        conn.close()

    dt = time.time() - t0
    print("\n" + "=" * 55)
    print(f"Terminé en {dt:.1f}s")
    print(f"  insérés    : {stats['inserted']}")
    print(f"  ignorés    : {stats['skipped']}")
    print(f"  sans bio   : {stats['no_content']}")
    print(f"  erreurs    : {stats['error']}")
    print(f"  chunks totaux insérés : {total_chunks}")
    if errors:
        print("\n⚠️  Détail des erreurs :")
        for name, msg in errors:
            print(f"   - {name} : {msg}")


if __name__ == "__main__":
    main()