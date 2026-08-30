import json, time, requests
from pathlib import Path

BASE = "https://universe-meeps.leagueoflegends.com/v1/fr_fr"
OUTPUT_DIR = Path("data/raw/universe_regions")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Slugs lus depuis search.json (comme pour les champions)
with open("search.json", encoding="utf-8") as f:
    factions = json.load(f).get("factions", [])
slugs = [fac["slug"] for fac in factions if fac.get("slug")]
print(f"{len(slugs)} factions à scraper")

ok = 0
for i, slug in enumerate(slugs, 1):
    url = f"{BASE}/factions/{slug}/index.json"
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        (OUTPUT_DIR / f"{slug}.json").write_text(r.text, encoding="utf-8")
        ok += 1
        print(f"[{i}/{len(slugs)}] {slug} OK")
    except Exception as e:
        print(f"[{i}/{len(slugs)}] {slug} ÉCHEC : {e}")
    time.sleep(0.5)

print(f"Terminé : {ok}/{len(slugs)}")