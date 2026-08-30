"""
Scraper Universe (champions) pour KnowTheLore.
Récupère la liste des champions depuis l'endpoint search,
puis télécharge la fiche complète de chaque champion.
"""

import json
import time
import requests
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

BASE = "https://universe-meeps.leagueoflegends.com/v1/fr_fr"
# ⚠️ URL à CONFIRMER par toi (vue avec ton espion réseau) :
SEARCH_URL = f"{BASE}/search/index.json"

OUTPUT_DIR = Path("data/raw/universe_champions")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_champion_slugs(search_file: str = "search.json") -> list[str]:
    """Lit les slugs de champions depuis le fichier search déjà capturé en local."""
    with open(search_file, encoding="utf-8") as f:
        data = json.load(f)
    slugs = [c["slug"] for c in data.get("champions", []) if c.get("slug")]
    logger.info(f"{len(slugs)} slugs lus depuis {search_file}")
    return slugs


def scrape_champion(slug: str) -> bool:
    """Télécharge la fiche d'un champion et la sauvegarde. Renvoie True si OK."""
    url = f"{BASE}/champions/{slug}/index.json"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        out = OUTPUT_DIR / f"{slug}.json"
        out.write_text(resp.text, encoding="utf-8")
        return True
    except Exception as e:
        logger.warning(f"Échec pour {slug} : {e}")
        return False


def main(delay: float = 0.5):
    slugs = get_champion_slugs()
    ok, total = 0, len(slugs)
    for idx, slug in enumerate(slugs, 1):
        logger.info(f"[{idx}/{total}] {slug}")
        if scrape_champion(slug):
            ok += 1
        if idx < total:
            time.sleep(delay)
    logger.info(f"Terminé : {ok}/{total} fiches récupérées dans {OUTPUT_DIR}")


if __name__ == "__main__":
    main()