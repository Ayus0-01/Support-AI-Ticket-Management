import hashlib
import time
from typing import Dict, Iterable, List, Optional, Sequence

from fastembed import TextEmbedding


# ---------------------------------------------------------
# M2 embedding configuration
# ---------------------------------------------------------

MODEL_NAME = "BAAI/bge-large-en-v1.5"
EMBEDDING_DIM = 1024

DEFAULT_BATCH_SIZE = 64
DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_SECONDS = 1.0


# Lazy-loaded model.
# This prevents every Django import from immediately
# downloading/loading the embedding model.
_embedding_model: Optional[TextEmbedding] = None


def _get_embedding_model() -> TextEmbedding:
    """
    Load the M2 KB embedding model lazily.
    """
    global _embedding_model

    if _embedding_model is None:
        _embedding_model = TextEmbedding(
            model_name=MODEL_NAME
        )

    return _embedding_model


def content_hash(
    content: str,
) -> str:
    """
    Return a deterministic SHA-256 hash for article/chunk content.

    M2 uses content hashes to avoid re-embedding unchanged
    knowledge-base content.
    """
    normalized = (
        content or ""
    ).strip()

    return (
        "sha256:"
        + hashlib.sha256(
            normalized.encode(
                "utf-8"
            )
        ).hexdigest()
    )


def validate_embedding(
    embedding: Sequence[float],
    *,
    expected_dim: int = EMBEDDING_DIM,
) -> List[float]:
    """
    Validate and normalize one embedding.

    M2 requires a fixed 1024-dimensional vector.

    Raises:
        ValueError when the embedding dimension is wrong.
    """
    if embedding is None:
        raise ValueError(
            "Embedding cannot be None."
        )

    vector = [
        float(value)
        for value in embedding
    ]

    actual_dim = len(vector)

    if actual_dim != expected_dim:
        raise ValueError(
            "Embedding dimension mismatch: "
            f"expected {expected_dim}, "
            f"received {actual_dim}."
        )

    return vector


def _embed_batch(
    texts: Sequence[str],
    *,
    batch_size: int,
    max_retries: int,
    backoff_seconds: float,
) -> List[List[float]]:
    """
    Embed one or more texts with retry/backoff.

    This function is intentionally separated from the public
    batch function so failures can be handled at batch level.
    """
    if not texts:
        return []

    model = _get_embedding_model()

    last_error = None

    for attempt in range(
        max_retries + 1
    ):
        try:
            raw_embeddings = list(
                model.embed(
                    list(texts),
                    batch_size=batch_size,
                )
            )

            if len(
                raw_embeddings
            ) != len(texts):
                raise ValueError(
                    "Embedding provider returned an unexpected "
                    "number of vectors: "
                    f"expected {len(texts)}, "
                    f"received {len(raw_embeddings)}."
                )

            validated = []

            for embedding in raw_embeddings:
                validated.append(
                    validate_embedding(
                        embedding
                    )
                )

            return validated

        except Exception as exc:
            last_error = exc

            if attempt >= max_retries:
                break

            delay = (
                backoff_seconds
                * (2 ** attempt)
            )

            time.sleep(
                delay
            )

    raise RuntimeError(
        "Embedding batch failed after "
        f"{max_retries + 1} attempts."
    ) from last_error


def generate_embeddings(
    texts: Sequence[str],
    *,
    batch_size: int = DEFAULT_BATCH_SIZE,
    max_retries: int = DEFAULT_MAX_RETRIES,
    backoff_seconds: float = DEFAULT_BACKOFF_SECONDS,
) -> List[List[float]]:
    """
    Generate embeddings for a sequence of texts.

    Features:
        - batches requests
        - retries failed batches
        - exponential backoff
        - validates every vector dimension
        - preserves input order

    Returns:
        List[List[float]]
    """
    if not texts:
        return []

    if batch_size <= 0:
        raise ValueError(
            "batch_size must be greater than zero."
        )

    if max_retries < 0:
        raise ValueError(
            "max_retries cannot be negative."
        )

    cleaned_texts = [
        (
            text or ""
        ).strip()
        for text in texts
    ]

    if any(
        not text
        for text in cleaned_texts
    ):
        raise ValueError(
            "Embedding input contains empty text."
        )

    embeddings: List[List[float]] = []

    for start in range(
        0,
        len(cleaned_texts),
        batch_size,
    ):
        batch = cleaned_texts[
            start : start + batch_size
        ]

        batch_embeddings = _embed_batch(
            batch,
            batch_size=batch_size,
            max_retries=max_retries,
            backoff_seconds=backoff_seconds,
        )

        embeddings.extend(
            batch_embeddings
        )

    return embeddings


def generate_chunk_embeddings(
    chunks: Sequence[Dict],
    *,
    batch_size: int = DEFAULT_BATCH_SIZE,
    max_retries: int = DEFAULT_MAX_RETRIES,
    backoff_seconds: float = DEFAULT_BACKOFF_SECONDS,
) -> List[Dict]:
    """
    Embed normalized chunk dictionaries.

    Expected input:

        {
            "chunk_index": 0,
            "heading_path": "...",
            "content": "...",
            "token_count": 123,
        }

    Returns copies enriched with:

        embedding
        embedding_model
        embedding_dim
        content_hash

    The original chunk dictionaries are not mutated.
    """
    if not chunks:
        return []

    texts = [
        (
            chunk.get(
                "content",
                "",
            )
            or ""
        ).strip()
        for chunk in chunks
    ]

    embeddings = generate_embeddings(
        texts,
        batch_size=batch_size,
        max_retries=max_retries,
        backoff_seconds=backoff_seconds,
    )

    enriched = []

    for chunk, embedding in zip(
        chunks,
        embeddings,
    ):
        updated = dict(
            chunk
        )

        updated[
            "embedding"
        ] = embedding

        updated[
            "embedding_model"
        ] = MODEL_NAME

        updated[
            "embedding_dim"
        ] = EMBEDDING_DIM

        updated[
            "content_hash"
        ] = content_hash(
            updated.get(
                "content",
                "",
            )
        )

        enriched.append(
            updated
        )

    return enriched


def should_reembed(
    *,
    new_content_hash: str,
    existing_content_hash: Optional[str],
    existing_embedding_model: Optional[str],
) -> bool:
    """
    Determine whether content needs to be re-embedded.

    Re-embedding is required when:
        - there is no previous hash
        - content changed
        - embedding model changed

    M2 explicitly uses content hashes to avoid unnecessary
    re-embedding of unchanged knowledge articles.
    """
    if not existing_content_hash:
        return True

    if (
        existing_content_hash
        != new_content_hash
    ):
        return True

    if (
        existing_embedding_model
        != MODEL_NAME
    ):
        return True

    return False


def prepare_chunks_for_embedding(
    chunks: Sequence[Dict],
    *,
    existing_chunk_map: Optional[Dict] = None,
) -> List[Dict]:
    """
    Determine which chunks require embedding.

    existing_chunk_map should map a stable key such as
    chunk_index to the existing MongoDB chunk document.

    Chunks that do not need re-embedding receive:

        "skip_embedding": True

    while changed/new chunks receive:

        "skip_embedding": False
    """
    existing_chunk_map = (
        existing_chunk_map
        or {}
    )

    prepared = []

    for chunk in chunks:
        updated = dict(
            chunk
        )

        current_hash = content_hash(
            updated.get(
                "content",
                "",
            )
        )

        existing = existing_chunk_map.get(
            updated.get(
                "chunk_index"
            )
        )

        if not existing:
            updated[
                "skip_embedding"
            ] = False

            updated[
                "content_hash"
            ] = current_hash

            prepared.append(
                updated
            )

            continue

        should_update = should_reembed(
            new_content_hash=current_hash,
            existing_content_hash=existing.get(
                "content_hash"
            ),
            existing_embedding_model=existing.get(
                "embedding_model"
            ),
        )

        updated[
            "skip_embedding"
        ] = not should_update

        updated[
            "content_hash"
        ] = current_hash

        prepared.append(
            updated
        )

    return prepared