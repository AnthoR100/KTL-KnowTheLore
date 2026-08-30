"""
Génération de réponses pour KnowTheLore.

Flux : question -> retrieval -> contexte (chunks réordonnés) -> LLM (Ollama) -> réponse.
Deux modes : answer() (réponse complète) et answer_stream() (streaming token par token).
"""

from __future__ import annotations

import json
import os

import requests
from dotenv import load_dotenv

from knowthelore.rag.retriever import retrieve, RetrievedChunk

load_dotenv()
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
LLM_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")


SYSTEM_PROMPT = """Tu es Aldric, un vieux voyageur qui a parcouru tout Runeterra et en a ramené des histoires plein la besace. Tu réponds en français, avec le ton chaleureux et vivant d'un conteur autour d'un feu de camp.

Règles à respecter :
- Appuie-toi uniquement sur les passages de lore fournis. N'invente aucun nom, événement ou détail absent des passages.
- Si les passages contiennent des éléments pertinents, même partiels, construis ta réponse à partir d'eux.
- Si l'information est partielle, dis ce que tu sais et admets que ta mémoire s'arrête là.
- Si les passages ne contiennent aucun élément en rapport avec la question, réponds : "Hmm, cette histoire-là, je ne l'ai pas dans mes carnets... Le lore dont je dispose ne me permet pas de répondre."
- Ne commence jamais par une phrase d'introduction méta ("je peux répondre", "d'après les éléments fournis", etc.). Entre directement dans le récit.
- Tu peux colorer tes réponses avec des formules de conteur : "on raconte que...", "j'ai entendu dire...", "un vieux sage de Demacia m'a confié...", "les habitants de Piltover murmurent que...". Ces formules doivent rester rares et naturelles, pas systématiques.
- Reste factuel sur le fond : le style est vivant, mais les faits viennent uniquement des passages fournis."""


def _build_context(chunks: list[RetrievedChunk]) -> tuple[str, list[str]]:
    """
    Construit le bloc de contexte à partir des chunks récupérés.
    Réordonne : par document (ordre de pertinence d'apparition), puis par
    chunk_index croissant à l'intérieur de chaque document (ordre de lecture).
    Renvoie (texte_du_contexte, liste_des_sources).
    """
    doc_order: list[str] = []
    by_doc: dict[str, list[RetrievedChunk]] = {}
    for c in chunks:
        if c.title not in by_doc:
            by_doc[c.title] = []
            doc_order.append(c.title)
        by_doc[c.title].append(c)

    blocs = []
    sources = []
    for title in doc_order:
        sources.append(title)
        ordered = sorted(by_doc[title], key=lambda x: x.chunk_index)
        texte = "\n".join(x.content for x in ordered)
        blocs.append(f"--- Source : {title} ---\n{texte}")

    return "\n\n".join(blocs), sources


def answer(question: str, k: int = 5, timeout: int = 120) -> dict:
    """
    Réponse complète (non streamée).
    Renvoie un dict : {answer, sources, chunks_used, no_context}.
    """
    chunks = retrieve(question, k=k)
    if not chunks:
        return {
            "answer": "Hmm, cette histoire-là, je ne l'ai pas dans mes carnets...",
            "sources": [],
            "chunks_used": 0,
            "no_context": True,
        }

    context, sources = _build_context(chunks)
    user_message = (
        f"Voici des passages de lore qui peuvent aider à répondre :\n\n"
        f"{context}\n\n"
        f"Question : {question}"
    )

    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": LLM_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                "stream": False,
                "options": {"temperature": 0.2, "num_ctx": 8192},
            },
            timeout=timeout,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"Appel LLM (Ollama) échoué : {e}") from e

    data = resp.json()
    content = data.get("message", {}).get("content")
    if not content:
        raise RuntimeError(f"Réponse LLM inattendue : {list(data.keys())}")

    return {
        "answer": content.strip(),
        "sources": sources,
        "chunks_used": len(chunks),
        "no_context": False,
    }


def answer_stream(question: str, k: int = 5, timeout: int = 120):
    """
    Générateur qui streame la réponse token par token.
    Émet des lignes JSON :
      {"type": "sources", "data": [...]}
      {"type": "token", "data": "..."}
      {"type": "done"}
    En cas d'erreur, émet {"type": "error", "data": "message"} puis s'arrête.
    """
    chunks = retrieve(question, k=k)
    if not chunks:
        yield json.dumps({"type": "sources", "data": []}) + "\n"
        yield json.dumps({"type": "token", "data": "Hmm, cette histoire-là, je ne l'ai pas dans mes carnets..."}) + "\n"
        yield json.dumps({"type": "done"}) + "\n"
        return

    context, sources = _build_context(chunks)
    user_message = (
        f"Voici des passages de lore qui peuvent aider à répondre :\n\n"
        f"{context}\n\n"
        f"Question : {question}"
    )

    # On envoie les sources en premier — le front peut les afficher
    # avant même que le LLM commence à répondre
    yield json.dumps({"type": "sources", "data": sources}) + "\n"

    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": LLM_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                "stream": True,
                "options": {"temperature": 0.2, "num_ctx": 8192},
            },
            stream=True,
            timeout=timeout,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        yield json.dumps({"type": "error", "data": str(e)}) + "\n"
        return

    for line in resp.iter_lines():
        if not line:
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue

        token = data.get("message", {}).get("content", "")
        if token:
            yield json.dumps({"type": "token", "data": token}) + "\n"

        if data.get("done"):
            break

    yield json.dumps({"type": "done"}) + "\n"