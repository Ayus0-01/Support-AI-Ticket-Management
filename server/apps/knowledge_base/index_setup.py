from typing import Dict, List, Optional

from pymongo import ASCENDING

from AIticket.db import article_chunks_collection

from .embeddings import EMBEDDING_DIM, MODEL_NAME


VECTOR_INDEX_NAME = "kb_vector_index"
TEXT_INDEX_NAME = "kb_text_index"


ARTICLE_CHUNKS_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            "article_id",
            "chunk_index",
            "content",
            "embedding",
            "embedding_model",
            "article_status",
        ],
        "properties": {
            "article_id": {
                "bsonType": "objectId",
            },
            "chunk_index": {
                "bsonType": "int",
                "minimum": 0,
            },
            "content": {
                "bsonType": "string",
                "minLength": 20,
            },
            "heading_path": {
                "bsonType": "string",
            },
            "article_title": {
                "bsonType": "string",
            },
            "article_status": {
                "enum": [
                    "DRAFT",
                    "PUBLISHED",
                    "ARCHIVED",
                ],
            },
            "category": {
                "bsonType": "string",
            },
            "sub_category": {
                "bsonType": "string",
            },
            "token_count": {
                "bsonType": "int",
                "minimum": 50,
                "maximum": 1200,
            },
            "embedding": {
                "bsonType": "array",
                "minItems": EMBEDDING_DIM,
                "maxItems": EMBEDDING_DIM,
                "items": {
                    "bsonType": "double",
                },
            },
            "embedding_model": {
                "bsonType": "string",
                "minLength": 1,
            },
            "embedding_dim": {
                "bsonType": "int",
                "minimum": EMBEDDING_DIM,
                "maximum": EMBEDDING_DIM,
            },
        },
    }
}


def configure_article_chunks_validator() -> Dict:
    """
    Apply the strict article_chunks MongoDB schema validator.

    Existing documents are not modified.
    Future inserts/updates are rejected when they violate
    the schema.
    """
    database = (
        article_chunks_collection.database
    )

    return database.command(
        {
            "collMod": article_chunks_collection.name,
            "validator": ARTICLE_CHUNKS_VALIDATOR,
            "validationLevel": "strict",
            "validationAction": "error",
        }
    )


def create_article_chunks_indexes() -> List[str]:
    """
    Create the normal MongoDB indexes required by M2.

    These are safe to call repeatedly because MongoDB reuses
    an existing index with the same name/specification.
    """
    created = []

    created.append(
        article_chunks_collection.create_index(
            [
                (
                    "article_id",
                    ASCENDING,
                ),
                (
                    "chunk_index",
                    ASCENDING,
                ),
            ],
            name="article_chunks_article_chunk",
            unique=True,
        )
    )

    created.append(
        article_chunks_collection.create_index(
            [
                (
                    "embedding_model",
                    ASCENDING,
                )
            ],
            name="article_chunks_embedding_model",
        )
    )

    return created


def list_search_indexes() -> List[Dict]:
    """
    Return all Atlas Search indexes currently defined
    on article_chunks.
    """
    return list(
        article_chunks_collection.list_search_indexes()
    )


def get_search_index(
    index_name: str,
) -> Optional[Dict]:
    """
    Return one Atlas Search index by name,
    or None when it does not exist.
    """
    for index in list_search_indexes():
        if index.get("name") == index_name:
            return index

    return None


def verify_search_index(
    index_name: str,
) -> Dict:
    """
    Verify existence, readiness and queryability of
    one Atlas Search index.
    """
    index = get_search_index(
        index_name
    )

    if index is None:
        return {
            "name": index_name,
            "exists": False,
            "ready": False,
            "queryable": False,
            "status": None,
            "type": None,
        }

    status = index.get(
        "status"
    )

    queryable = bool(
        index.get(
            "queryable",
            False,
        )
    )

    return {
        "name": index_name,
        "exists": True,
        "ready": status == "READY",
        "queryable": queryable,
        "status": status,
        "type": index.get(
            "type"
        ),
    }


def verify_required_search_indexes() -> Dict:
    """
    Verify that both required M2 Atlas Search indexes
    exist and are ready/queryable.
    """
    vector = verify_search_index(
        VECTOR_INDEX_NAME
    )

    text = verify_search_index(
        TEXT_INDEX_NAME
    )

    return {
        "vector": vector,
        "text": text,
        "all_ready": (
            vector["exists"]
            and vector["ready"]
            and vector["queryable"]
            and text["exists"]
            and text["ready"]
            and text["queryable"]
        ),
    }


def create_vector_search_index() -> Dict:
    """
    Create the M2 vector index only when it does not
    already exist.

    This prevents duplicate Atlas indexes.
    """
    existing = get_search_index(
        VECTOR_INDEX_NAME
    )

    if existing is not None:
        return {
            "created": False,
            "existing": True,
            "index": existing,
        }

    definition = {
        "fields": [
            {
                "type": "vector",
                "path": "embedding",
                "numDimensions": EMBEDDING_DIM,
                "similarity": "cosine",
            },
            {
                "type": "filter",
                "path": "article_status",
            },
            {
                "type": "filter",
                "path": "category",
            },
            {
                "type": "filter",
                "path": "embedding_model",
            },
        ]
    }

    result = (
        article_chunks_collection.create_search_index(
            {
                "name": VECTOR_INDEX_NAME,
                "type": "vectorSearch",
                "definition": definition,
            }
        )
    )

    return {
        "created": True,
        "existing": False,
        "result": result,
    }


def create_text_search_index() -> Dict:
    """
    Create the M2 keyword search index only when it does
    not already exist.

    This prevents duplicate Atlas indexes.
    """
    existing = get_search_index(
        TEXT_INDEX_NAME
    )

    if existing is not None:
        return {
            "created": False,
            "existing": True,
            "index": existing,
        }

    definition = {
        "mappings": {
            "dynamic": False,
            "fields": {
                "content": {
                    "type": "string",
                    "analyzer": "lucene.standard",
                },
                "heading_path": {
                    "type": "string",
                    "analyzer": "lucene.standard",
                },
                "article_title": {
                    "type": "string",
                    "analyzer": "lucene.standard",
                },
                "article_status": {
                    "type": "token",
                },
                "category": {
                    "type": "token",
                },
            },
        }
    }

    result = (
        article_chunks_collection.create_search_index(
            {
                "name": TEXT_INDEX_NAME,
                "type": "search",
                "definition": definition,
            }
        )
    )

    return {
        "created": True,
        "existing": False,
        "result": result,
    }


def configure_all_article_chunk_indexes() -> Dict:
    """
    Configure the validator and normal MongoDB indexes.

    Atlas Search indexes are intentionally NOT recreated here.
    Their existing definitions are verified separately.
    """
    validator_result = (
        configure_article_chunks_validator()
    )

    normal_indexes = (
        create_article_chunks_indexes()
    )

    atlas_status = (
        verify_required_search_indexes()
    )

    return {
        "validator": validator_result,
        "normal_indexes": normal_indexes,
        "atlas_indexes": atlas_status,
        "vector_index": VECTOR_INDEX_NAME,
        "text_index": TEXT_INDEX_NAME,
        "embedding_model": MODEL_NAME,
        "embedding_dimension": EMBEDDING_DIM,
    }