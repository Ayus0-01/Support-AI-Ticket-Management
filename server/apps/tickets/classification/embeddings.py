from fastembed import TextEmbedding
from .preprocessing import preprocess_ticket


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_embedding_model = TextEmbedding(
    model_name=MODEL_NAME
)


def generate_embedding(subject, description):
    """
    Generate a numerical embedding for a ticket.

    The ticket is preprocessed before embedding.
    The subject is intentionally repeated so that it
    has greater influence than the description.
    """

    cleaned_ticket = preprocess_ticket(
        subject,
        description,
    )

    subject = cleaned_ticket["subject"]
    description = cleaned_ticket["description"]

    text = (
        f"Subject: {subject}\n"
        f"Subject: {subject}\n"
        f"Description: {description}"
    )

    embedding = next(
        _embedding_model.embed([text])
    )

    return embedding.tolist()