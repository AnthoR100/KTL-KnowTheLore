"""
Option D — construction des chunks "index global" pour KnowTheLore.

But : permettre aux questions agrégées ("combien de régions ?", "liste les
champions") de remonter un chunk contenant la LISTE et le DÉCOMPTE, calculés
depuis la base. Ces chunks ne sont PAS du lore : c'est un inventaire de ce qui
est présent dans les archives.

ÉTAPE 1 (ce fichier) : lire la base, classer les documents en régions /
champions, composer les deux textes d'index et les AFFICHER. AUCUNE écriture en
base. Sert à valider le discriminant et les décomptes avant d'insérer quoi que
ce soit. À lancer après ingest_all.py et ingest_all_regions.py.

Discriminant utilisé (validé sur la base réelle) : l'URL source publique
Universe contient '/champion/' pour un champion, '/region/' pour une région
(au singulier). Tout document non classé est signalé, jamais ignoré en silence.

Placement suggéré : knowthelore/ingestion/build_index_chunk.py
Lancement : poetry run python -m knowthelore.ingestion.build_index_chunk
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import psycopg
from psycopg.types.json import Json
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from knowthelore.embeddings.embedder import embed_text

# Charge .env (le fichier réel s'appelle .env ; load_dotenv() le cherche en
# remontant l'arborescence). À uniformiser avec les autres scripts du projet.
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL n'est pas défini (vérifie ton .env)")
MODEL_NAME = os.getenv("EMBEDDING_MODEL", "bge-m3")

# Spécification des deux documents index. source_type='index' pour qu'ils ne
# soient pas relus comme corpus au prochain rebuild (fetch_documents filtre
# 'riot_universe'). source_url interne et stable -> insertion idempotente.
INDEX_SPECS = {
    "regions": {
        "source_url": "internal://index/regions",
        "title": "Inventaire des régions de Runeterra",
    },
    "champions": {
        "source_url": "internal://index/champions",
        "title": "Inventaire des champions de League of Legends",
    },
}


def _classify(source_url: str) -> str:
    """Classe un document d'après son URL source. Hypothèse à valider."""
    u = (source_url or "").lower()
    if "/champion/" in u:
        return "champion"
    if "/region/" in u:
        return "region"
    return "autre"


def _short_name(title: str) -> str:
    """'Ahri, Renard à neuf queues' -> 'Ahri'. Cosmétique, ajustable."""
    return title.split(",")[0].strip()


def fetch_documents(conn: psycopg.Connection) -> list[tuple[str, str, str]]:
    """Renvoie (title, source_url, classe) pour les documents riot_universe."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT title, source_url FROM documents "
            "WHERE source_type = 'riot_universe' ORDER BY title;"
        )
        rows = cur.fetchall()
    return [(t, u, _classify(u)) for (t, u) in rows]


def _names(titles: list[str]) -> list[str]:
    """Noms courts dédoublonnés et triés (insensible à la casse)."""
    return sorted({_short_name(t) for t in titles}, key=str.casefold)


def compose_regions(names: list[str]) -> str:
    return (
        f"Inventaire des régions (factions) de Runeterra présentes dans ces "
        f"archives. Il y a actuellement {len(names)} régions répertoriées : "
        f"{', '.join(names)}."
    )


def compose_champions(names: list[str]) -> str:
    return (
        f"Inventaire des champions de League of Legends présents dans ces "
        f"archives. Il y a actuellement {len(names)} champions répertoriés : "
        f"{', '.join(names)}."
    )


def build_index_texts(conn: psycopg.Connection) -> dict:
    docs = fetch_documents(conn)
    regions_names = _names([t for (t, _u, c) in docs if c == "region"])
    champions_names = _names([t for (t, _u, c) in docs if c == "champion"])
    autres = [(t, u) for (t, u, c) in docs if c == "autre"]
    return {
        "regions_names": regions_names,
        "champions_names": champions_names,
        "autres": autres,
        "regions_text": compose_regions(regions_names),
        "champions_text": compose_champions(champions_names),
    }


def _store_index(
    conn: psycopg.Connection, *, kind: str, source_url: str, title: str,
    text: str, names: list[str],
) -> None:
    """
    Insère (ou remplace) un document index : document + 1 chunk + 1 embedding.
    Idempotent : supprime d'abord l'index existant de même source_url (CASCADE
    emporte chunk + embedding), puis ré-insère. L'embedding est calculé AVANT
    la transaction : si Ollama échoue, rien n'est écrit.
    """
    regions = names if kind == "regions" else []
    champions = names if kind == "champions" else []
    raw = {"generated": True, "kind": kind, "count": len(names), "names": names}
    doc_meta = {"index": True, "kind": kind, "language": "fr"}
    chunk_meta = {"champions": champions, "regions": regions, "passage_type": "index"}

    vector = embed_text(text)  # peut lever EmbeddingError
    vec_str = "[" + ",".join(map(str, vector)) + "]"

    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute("DELETE FROM documents WHERE source_url = %s;", (source_url,))
            cur.execute(
                """
                INSERT INTO documents
                    (source_type, source_url, title, author, published_date,
                     raw_content, metadata, is_official, is_canon)
                VALUES ('index', %s, %s, NULL, NULL, %s, %s, FALSE, FALSE)
                RETURNING id;
                """,
                (source_url, title, Json(raw), Json(doc_meta)),
            )
            document_id = cur.fetchone()[0]
            cur.execute(
                """
                INSERT INTO chunks (document_id, chunk_index, content, token_count, metadata)
                VALUES (%s, 0, %s, %s, %s) RETURNING id;
                """,
                (document_id, text, len(text) // 4, Json(chunk_meta)),
            )
            chunk_id = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO embeddings (chunk_id, vector, model_name) "
                "VALUES (%s, %s::vector, %s);",
                (chunk_id, vec_str, MODEL_NAME),
            )


def store_all(conn: psycopg.Connection, data: dict) -> None:
    """Écrit les deux documents index à partir d'un build déjà calculé."""
    _store_index(
        conn, kind="regions", **INDEX_SPECS["regions"],
        text=data["regions_text"], names=data["regions_names"],
    )
    _store_index(
        conn, kind="champions", **INDEX_SPECS["champions"],
        text=data["champions_text"], names=data["champions_names"],
    )


def _print_summary(data: dict) -> None:
    print("=" * 60)
    print(f"Régions classées    : {len(data['regions_names'])}  (attendu : 13)")
    print(f"Champions classés   : {len(data['champions_names'])}  (attendu : 173)")
    print(f"Non classés (autre) : {len(data['autres'])}")
    if data["autres"]:
        print("\n⚠️  Documents non classés (à examiner) :")
        for t, u in data["autres"][:20]:
            print(f"   - {t}  [{u}]")
    print("\n--- TEXTE INDEX RÉGIONS ---")
    print(data["regions_text"])
    print("\n--- TEXTE INDEX CHAMPIONS (aperçu 400 car.) ---")
    apercu = data["champions_text"]
    print(apercu[:400] + (" ..." if len(apercu) > 400 else ""))
    print(f"\nlongueur texte champions : {len(apercu)} caractères")


def run(write: bool = False) -> int:
    """
    Construit les deux index. Si write=True, les écrit puis VÉRIFIE en relisant
    dans une nouvelle connexion. Renvoie le nombre de documents index relus
    (0 en lecture seule ou si l'écriture est refusée). Appelable depuis un
    script chapeau d'ingestion.

    autocommit=True : évite le piège du SELECT initial qui ouvrait une
    transaction laissée ouverte, transformant transaction() en simple savepoint
    jamais committé (les insertions disparaissaient à la fermeture).
    """
    conn = psycopg.connect(DATABASE_URL, autocommit=True)
    try:
        data = build_index_texts(conn)
        _print_summary(data)
        if not write:
            print("\n(Mode lecture seule. Ajoute --write pour insérer en base.)")
            return 0
        if data["autres"]:
            print("\n⛔ Des documents sont non classés : écriture annulée. "
                  "Corrige le discriminant d'abord.")
            return 0
        store_all(conn, data)
    finally:
        conn.close()

    # Vérification indépendante, dans une NOUVELLE connexion.
    with psycopg.connect(DATABASE_URL, autocommit=True) as check:
        with check.cursor() as cur:
            cur.execute("SELECT count(*) FROM documents WHERE source_type = 'index';")
            persisted = cur.fetchone()[0]
    if persisted == 2:
        print(f"\n✅ Vérifié dans une nouvelle connexion : "
              f"{persisted} documents index présents.")
    else:
        print(f"\n⚠️  Anomalie : {persisted} document(s) index relus "
              f"(attendu 2). À investiguer, rien n'est garanti.")
    return persisted


if __name__ == "__main__":
    run(write="--write" in sys.argv)