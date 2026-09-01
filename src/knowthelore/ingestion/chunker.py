"""
Chunker pour KnowTheLore.

Rôle : découper un texte (déjà nettoyé par le parser) en morceaux de taille
maîtrisée, avec un léger recouvrement, en respectant les frontières naturelles
(paragraphes puis phrases) plutôt qu'en coupant au milieu des mots.

Travaille en CARACTÈRES (pas en tokens) : c'est une approximation assumée,
à recalibrer quand le modèle d'embeddings sera fixé. Voir les réserves plus bas.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Chunk:
    """Un morceau de texte prêt à être encodé en embedding."""
    text: str
    index: int          # position du chunk dans le document (0, 1, 2...)
    char_count: int


# Valeurs de départ, en caractères. ~2000 car. ≈ ~500 tokens (très approximatif).
DEFAULT_CHUNK_SIZE = 2000
DEFAULT_OVERLAP = 200


def _split_sentences(text: str) -> list[str]:
    """Découpe grossièrement en phrases (sur . ! ? suivis d'un espace)."""
    # On garde le séparateur collé à la phrase qui précède.
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p]


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
) -> list[Chunk]:
    """
    Découpe `text` en chunks de ~chunk_size caractères, avec `overlap`
    caractères de recouvrement entre chunks consécutifs.

    Stratégie : on regroupe d'abord par paragraphes (préservés par le parser).
    Si un paragraphe seul dépasse chunk_size, on le redécoupe par phrases.
    """
    if not text or not text.strip():
        return []

    # 1. Unité de base : le paragraphe (séparé par les sauts du parser)
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    # 2. On éclate les paragraphes trop longs en phrases
    units: list[str] = []
    for para in paragraphs:
        if len(para) <= chunk_size:
            units.append(para)
        else:
            sentences = _split_sentences(para)
            buffer = ""
            for sent in sentences:
                if len(buffer) + len(sent) + 1 <= chunk_size:
                    buffer = f"{buffer} {sent}".strip()
                else:
                    if buffer:
                        units.append(buffer)
                    # Phrase seule plus longue que chunk_size : on la garde
                    # telle quelle (coupe en dernier recours évitée ici).
                    buffer = sent
            if buffer:
                units.append(buffer)

    # 3. On regroupe les unités en chunks proches de chunk_size
    chunks: list[Chunk] = []
    current = ""
    for unit in units:
        if not current:
            current = unit
        elif len(current) + len(unit) + 2 <= chunk_size:
            current = f"{current}\n\n{unit}"
        else:
            chunks.append(current)
            # Recouvrement : on repart avec la fin du chunk précédent
            tail = current[-overlap:] if overlap > 0 else ""
            current = f"{tail}\n\n{unit}".strip() if tail else unit

    if current:
        chunks.append(current)

    # 4. Emballage en objets Chunk avec leur index
    return [
        Chunk(text=c.strip(), index=i, char_count=len(c.strip()))
        for i, c in enumerate(chunks)
    ]


if __name__ == "__main__":
    import sys
    from knowthelore.ingestion.parser import parse_universe_champion

    path = sys.argv[1] if len(sys.argv) > 1 else "data/raw/universe_champions/ahri.json"
    doc = parse_universe_champion(path)
    if doc is None:
        print("Aucune biographie exploitable.")
        sys.exit()

    chunks = chunk_text(doc.content)
    print(f"Document : {doc.title}")
    print(f"Longueur totale : {len(doc.content)} caractères")
    print(f"Nombre de chunks : {len(chunks)}")
    print("=" * 55)
    for c in chunks:
        print(f"\n--- chunk {c.index} ({c.char_count} car.) ---")
        print(c.text[:200], "..." if len(c.text) > 200 else "")