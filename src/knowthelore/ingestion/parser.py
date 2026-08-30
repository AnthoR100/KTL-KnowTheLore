"""
Parsing des fiches champion Universe pour KnowTheLore.

Rôle : lire un JSON de champion capturé depuis l'API Universe, en extraire
la biographie complète (champion.biography.full), la nettoyer (HTML, entités,
espaces insécables) et renvoyer un ParsedDocument prêt pour le chunking.
Ne touche ni à la base de données ni aux embeddings.
"""

from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ParsedDocument:
    """Représentation propre d'un document lore, prête pour le chunking."""
    source_type: str          # "riot_universe"
    source_url: str           # URL stable de la page (à vérifier)
    title: str                # "Ahri, Renard à neuf queues"
    content: str              # biographie nettoyée
    language: str             # "fr_FR"
    is_official: bool
    is_canon: bool
    metadata: dict = field(default_factory=dict)


def _clean_biography(raw: str) -> str:
    """
    Nettoie le HTML de la biographie Universe :
    - convertit les frontières de paragraphe </p> en sauts de paragraphe
    - retire toutes les autres balises HTML (robuste : <p>, <i>, et tout autre)
    - décode les entités HTML (&nbsp;, &amp;, etc.)
    - neutralise les espaces insécables
    - normalise les espaces sans détruire les paragraphes
    """
    # 1. Marquer les fins de paragraphe AVANT de retirer les balises
    text = re.sub(r"</p\s*>", "\n\n", raw, flags=re.IGNORECASE)

    # 2. Retirer toute balise restante (<p>, <i>, et tout imprévu)
    text = re.sub(r"<[^>]+>", "", text)

    # 3. Décoder les entités HTML (&nbsp; -> espace insécable, etc.)
    text = html.unescape(text)

    # 4. Neutraliser les espaces insécables
    text = text.replace("\xa0", " ")

    # 5. Normaliser les espaces : espaces/tabs multiples -> un seul,
    #    mais on préserve les sauts de paragraphe.
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)        # espaces en début de ligne
    text = re.sub(r"[ \t]+\n", "\n", text)        # espaces en fin de ligne
    text = re.sub(r"\n{3,}", "\n\n", text)        # max 2 sauts d'affilée
    return text.strip()


def parse_universe_champion(path: str | Path) -> ParsedDocument | None:
    """
    Lit une fiche champion Universe et renvoie un ParsedDocument.
    Renvoie None si la biographie est absente ou vide.
    """
    path = Path(path)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    champ = data.get("champion", {})
    name = champ.get("name") or data.get("name")
    title = champ.get("title", "")
    slug = champ.get("slug") or data.get("id")

    bio = champ.get("biography", {})
    raw_full = bio.get("full", "") if isinstance(bio, dict) else ""

    # Garde-fou : pas de biographie exploitable
    if not raw_full or not slug:
        return None

    content = _clean_biography(raw_full)
    if not content:
        return None

    faction = champ.get("associated-faction-slug", "") or ""
    regions = [faction] if faction and faction != "unaffiliated" else []

    # races / roles : listes de dicts {name, slug} -> on garde les noms
    races = [r.get("name") for r in champ.get("races", []) if r.get("name")]
    roles = [r.get("name") for r in champ.get("roles", []) if r.get("name")]

    return ParsedDocument(
        source_type="riot_universe",
        source_url=f"https://universe.leagueoflegends.com/fr_FR/champion/{slug}/",
        title=f"{name}, {title}" if title else name,
        content=content,
        language="fr_FR",
        is_official=True,
        is_canon=True,
        metadata={
            "champions": [name],
            "regions": regions,
            "races": races,
            "roles": roles,
            "passage_type": "biography",
        },
    )

def parse_universe_region(path: str | Path) -> ParsedDocument | None:
    """
    Lit une fiche faction/région Universe et renvoie un ParsedDocument.
    Le lore est dans faction.overview.short (vérifié sur Ionia).
    Renvoie None si pas de texte exploitable.
    """
    path = Path(path)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    faction = data.get("faction", {})
    name = faction.get("name") or data.get("name")
    slug = faction.get("slug") or data.get("id")

    overview = faction.get("overview", {})
    raw_text = overview.get("short", "") if isinstance(overview, dict) else ""

    if not raw_text or not slug:
        return None

    content = _clean_biography(raw_text)  # même nettoyage HTML que les bios
    if not content:
        return None

    return ParsedDocument(
        source_type="riot_universe",
        source_url=f"https://universe.leagueoflegends.com/fr_FR/region/{slug}/",
        title=name,
        content=content,
        language="fr_FR",
        is_official=True,
        is_canon=True,
        metadata={
            "champions": [],            # laissé vide, comme décidé
            "regions": [slug],
            "passage_type": "region",
        },
    )

if __name__ == "__main__":
    import sys
    test_path = sys.argv[1] if len(sys.argv) > 1 else "data/raw/universe_champions/ahri.json"
    doc = parse_universe_champion(test_path)
    if doc is None:
        print("Aucune biographie exploitable dans ce fichier.")
    else:
        print("source_type :", doc.source_type)
        print("source_url  :", doc.source_url)
        print("title       :", doc.title)
        print("language    :", doc.language)
        print("official    :", doc.is_official, "| canon :", doc.is_canon)
        print("metadata    :", doc.metadata)
        print("longueur    :", len(doc.content), "caractères")
        print("--- content (début) ---")
        print(doc.content[:400])