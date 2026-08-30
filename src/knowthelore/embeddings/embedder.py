"""
Module d'embeddings pour KnowTheLore.

Rôle : transformer du texte en vecteurs via BGE-M3 servi par Ollama.
Format de réponse confirmé sur l'environnement réel : /api/embed renvoie
{"embeddings": [[...1024 valeurs...]]}.
"""

from __future__ import annotations

import os
import requests

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "bge-m3")
EXPECTED_DIM = int(os.getenv("EMBEDDING_DIM", "1024"))


class EmbeddingError(RuntimeError):
    """Erreur lors de la génération d'un embedding."""


def embed_text(text: str, timeout: int = 60) -> list[float]:
    """
    Renvoie le vecteur (1024 floats) correspondant à `text`.
    Lève EmbeddingError en cas de problème (réseau, format, dimension).
    """
    if not text or not text.strip():
        raise EmbeddingError("Texte vide : rien à encoder.")

    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/embed",
            json={"model": EMBEDDING_MODEL, "input": text},
            timeout=timeout,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        raise EmbeddingError(f"Appel Ollama échoué : {e}") from e

    data = resp.json()
    if "embeddings" not in data or not data["embeddings"]:
        raise EmbeddingError(f"Réponse inattendue d'Ollama : {list(data.keys())}")

    vector = data["embeddings"][0]

    # Garde-fou : la dimension doit correspondre au schéma de la base
    if len(vector) != EXPECTED_DIM:
        raise EmbeddingError(
            f"Dimension {len(vector)} != {EXPECTED_DIM} attendue. "
            f"Modèle ou schéma incohérent ?"
        )

    return vector


def embed_batch(texts: list[str], timeout: int = 120) -> list[list[float]]:
    """
    Encode plusieurs textes. BGE-M3 via Ollama accepte une liste en 'input',
    ce qui évite un aller-retour réseau par texte.
    """
    clean = [t for t in texts if t and t.strip()]
    if not clean:
        return []

    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/embed",
            json={"model": EMBEDDING_MODEL, "input": clean},
            timeout=timeout,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        raise EmbeddingError(f"Appel Ollama échoué : {e}") from e

    data = resp.json()
    vectors = data.get("embeddings")
    if not vectors or len(vectors) != len(clean):
        raise EmbeddingError(
            f"Nombre de vecteurs ({len(vectors) if vectors else 0}) "
            f"!= nombre de textes ({len(clean)})."
        )

    for v in vectors:
        if len(v) != EXPECTED_DIM:
            raise EmbeddingError(f"Dimension {len(v)} != {EXPECTED_DIM} attendue.")

    return vectors


if __name__ == "__main__":
    # Test unitaire
    v = embed_text("Ahri est une vastaya d'Ionia.")
    print("embed_text OK — dimension :", len(v))

    batch = embed_batch([
        "Aatrox était un Darkin.",
        "Zaun est une cité souterraine.",
    ])
    print("embed_batch OK — nombre de vecteurs :", len(batch))
    print("dimension de chaque :", [len(v) for v in batch])