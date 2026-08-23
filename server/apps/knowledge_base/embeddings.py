from fastembed import TextEmbedding

MODEL_NAME = "BAAI/bge-large-en-v1.5"

_embedding_model = TextEmbedding(
    model_name=MODEL_NAME
)

def generate_embedding(text):
    if not text or not text.strip():
        raise ValueError(
            "Cannot generate an embedding for empty text."
        )
    vector = next(
        _embedding_model.embed([text])
    )
    return vector.tolist()