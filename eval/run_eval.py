"""
Évaluation manuelle du pipeline RAG KnowTheLore.

Rejoue le jeu de questions (eval/questions.json) contre le pipeline réel
(retriever + générateur), et produit un rapport Markdown pour vérification
manuelle : question, faits attendus, réponse générée, sources retournées.

Le scoring automatique d'une réponse en langue naturelle n'est pas fiable ;
ce script prépare la comparaison côte à côte, la vérification reste manuelle
(case à cocher OK / Partiel / KO dans le rapport généré).

Lancement :
    poetry run python eval/run_eval.py
    poetry run python eval/run_eval.py --category lore_ambigu
    poetry run python eval/run_eval.py --id ambigu-01
    poetry run python eval/run_eval.py --retrieval-only   # pas d'appel LLM, juste les sources
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from knowthelore.rag.generator import answer
from knowthelore.rag.retriever import retrieve

QUESTIONS_PATH = Path(__file__).parent / "questions.json"
RESULTS_DIR = Path(__file__).parent / "results"


def load_questions() -> list[dict]:
    return json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))


def run_one(question: str, k: int, retrieval_only: bool) -> dict:
    if retrieval_only:
        chunks = retrieve(question, k=k)
        return {
            "answer": None,
            "sources": [
                f"{c.title} (chunk {c.chunk_index}, sim={c.similarity:.3f})"
                for c in chunks
            ],
            "chunks_used": len(chunks),
            "no_context": len(chunks) == 0,
        }
    return answer(question, k=k)


def format_report(rows: list[tuple[dict, dict]]) -> str:
    lines = [f"# Rapport d'évaluation KnowTheLore — {datetime.now():%Y-%m-%d %H:%M}", ""]

    by_category: dict[str, list[tuple[dict, dict]]] = {}
    for q, r in rows:
        by_category.setdefault(q["category"], []).append((q, r))

    for category, items in by_category.items():
        lines.append(f"## {category} ({len(items)} questions)")
        lines.append("")
        for q, r in items:
            lines.append(f"### {q['id']} — {q['question']}")
            lines.append(f"- **Attendu :** {q['expected']}")
            if q.get("notes"):
                lines.append(f"- **Note :** {q['notes']}")
            if r["answer"] is not None:
                lines.append(f"- **Réponse générée :** {r['answer']}")
            sources = ", ".join(r["sources"]) if r["sources"] else "(aucune)"
            lines.append(f"- **Sources retournées :** {sources}")
            lines.append(
                f"- **Chunks utilisés :** {r['chunks_used']}  |  "
                f"**Sans contexte :** {r['no_context']}"
            )
            lines.append("- **Verdict manuel :** ☐ OK   ☐ Partiel   ☐ KO   — ")
            lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--category",
        help="Ne rejouer qu'une catégorie (lore_simple, lore_ambigu, questions_agregees, hors_lore)",
    )
    parser.add_argument("--id", help="Ne rejouer qu'une question précise (par id)")
    parser.add_argument("--k", type=int, default=5, help="Nombre de chunks à récupérer (défaut : 5)")
    parser.add_argument(
        "--retrieval-only",
        action="store_true",
        help="N'appelle pas le LLM, affiche seulement les sources retrouvées",
    )
    parser.add_argument("--out", help="Chemin du rapport markdown (défaut : eval/results/<timestamp>.md)")
    args = parser.parse_args()

    questions = load_questions()
    if args.category:
        questions = [q for q in questions if q["category"] == args.category]
    if args.id:
        questions = [q for q in questions if q["id"] == args.id]
    if not questions:
        print("Aucune question ne correspond aux filtres.", file=sys.stderr)
        sys.exit(1)

    rows: list[tuple[dict, dict]] = []
    for i, q in enumerate(questions, 1):
        print(f"[{i}/{len(questions)}] {q['id']} : {q['question']}")
        try:
            r = run_one(q["question"], k=args.k, retrieval_only=args.retrieval_only)
        except RuntimeError as e:
            r = {"answer": f"[ERREUR] {e}", "sources": [], "chunks_used": 0, "no_context": True}
        rows.append((q, r))

    RESULTS_DIR.mkdir(exist_ok=True)
    out_path = Path(args.out) if args.out else RESULTS_DIR / f"eval_{datetime.now():%Y%m%d_%H%M%S}.md"
    out_path.write_text(format_report(rows), encoding="utf-8")
    print(f"\nRapport écrit : {out_path}")


if __name__ == "__main__":
    main()
