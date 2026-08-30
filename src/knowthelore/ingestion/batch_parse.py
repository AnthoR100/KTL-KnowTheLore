"""
Parcours du lot complet : parse toutes les fiches Universe et produit un rapport.
Ne touche ni à la base ni aux embeddings : il lit, parse, compte, et mesure.

Objectifs :
- repérer les fichiers sans biographie exploitable (parser -> None)
- mesurer les longueurs de texte (pour concevoir le chunking sans deviner)
"""

from __future__ import annotations

import statistics
from pathlib import Path

# parser.py est dans le même dossier : import direct
from parser import parse_universe_champion

INPUT_DIR = Path("data/raw/universe_champions")


def main():
    files = sorted(INPUT_DIR.glob("*.json"))
    if not files:
        print(f"Aucun fichier .json trouvé dans {INPUT_DIR}")
        return

    parsed = []      # (nom, longueur)
    failed = []      # noms de fichiers sans bio exploitable

    for path in files:
        doc = parse_universe_champion(path)
        if doc is None:
            failed.append(path.name)
        else:
            parsed.append((doc.title, len(doc.content)))

    total = len(files)
    ok = len(parsed)

    print("=" * 55)
    print(f"  Fichiers trouvés : {total}")
    print(f"  Parsés avec succès : {ok}")
    print(f"  Échecs (bio vide/absente) : {len(failed)}")
    print("=" * 55)

    if failed:
        print("\n⚠️  Fichiers sans biographie exploitable :")
        for name in failed:
            print("   -", name)

    if parsed:
        longueurs = [n for _, n in parsed]
        print("\n📏 Longueurs (en caractères) :")
        print(f"   min     : {min(longueurs)}")
        print(f"   max     : {max(longueurs)}")
        print(f"   moyenne : {round(statistics.mean(longueurs))}")
        print(f"   médiane : {round(statistics.median(longueurs))}")

        # Le plus court et le plus long, pour repérer les cas extrêmes
        plus_court = min(parsed, key=lambda x: x[1])
        plus_long = max(parsed, key=lambda x: x[1])
        print(f"\n   Plus courte : {plus_court[0]} ({plus_court[1]} car.)")
        print(f"   Plus longue : {plus_long[0]} ({plus_long[1]} car.)")

        # Répartition par tranches (utile pour le chunking)
        tranches = {"< 2000": 0, "2000-4000": 0, "4000-6000": 0, "> 6000": 0}
        for n in longueurs:
            if n < 2000:
                tranches["< 2000"] += 1
            elif n < 4000:
                tranches["2000-4000"] += 1
            elif n < 6000:
                tranches["4000-6000"] += 1
            else:
                tranches["> 6000"] += 1
        print("\n📊 Répartition par longueur :")
        for tranche, count in tranches.items():
            print(f"   {tranche:>10} car. : {count} champions")


if __name__ == "__main__":
    main()