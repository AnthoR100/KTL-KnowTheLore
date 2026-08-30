"""
Ingestion des régions Universe : applique ingest_region à toutes les fiches faction.
Calqué sur ingest_all.py. Chaque région dans sa propre transaction.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import psycopg
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from knowthelore.ingestion.ingest import ingest_region

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL n'est pas défini (vérifie ton .env)")
INPUT_DIR = Path("data/raw/universe_regions")


def main():
    files = sorted(INPUT_DIR.glob("*.json"))
    if not files:
        print(f"Aucun fichier dans {INPUT_DIR}")
        return

    stats = {"inserted": 0, "skipped": 0, "no_content": 0, "error": 0}
    total_chunks = 0
    errors, empties = [], []

    conn = psycopg.connect(DATABASE_URL)
    try:
        for idx, path in enumerate(files, 1):
            try:
                statut, n = ingest_region(path, conn)
                stats[statut] += 1
                total_chunks += n
                if statut == "no_content":
                    empties.append(path.stem)
                print(f"[{idx}/{len(files)}] {path.stem:18s} -> {statut} ({n} chunks)")
            except Exception as e:
                stats["error"] += 1
                errors.append((path.stem, str(e)))
                print(f"[{idx}/{len(files)}] {path.stem:18s} -> ERREUR : {e}")
    finally:
        conn.close()

    print("\n" + "=" * 50)
    print(f"  insérées   : {stats['inserted']}")
    print(f"  ignorées   : {stats['skipped']}")
    print(f"  sans lore  : {stats['no_content']}")
    print(f"  erreurs    : {stats['error']}")
    print(f"  chunks insérés : {total_chunks}")
    if empties:
        print("\n⚠️  Factions sans lore exploitable :", ", ".join(empties))
    if errors:
        print("\n⚠️  Erreurs :")
        for name, msg in errors:
            print(f"   - {name} : {msg}")


if __name__ == "__main__":
    main()