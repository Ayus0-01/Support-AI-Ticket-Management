from AIticket.db import article_chunks_collection


query = "VPN connection timeout"

pipeline = [
    {
        "$search": {
            "index": "kb_text_index",
            "compound": {
                "filter": [
                    {
                        "equals": {
                            "path": "article_status",
                            "value": "DRAFT",
                        }
                    }
                ],
                "should": [
                    {
                        "text": {
                            "query": query,
                            "path": "content",
                        }
                    },
                    {
                        "text": {
                            "query": query,
                            "path": "heading_path",
                            "score": {
                                "boost": {
                                    "value": 2
                                }
                            },
                        }
                    },
                    {
                        "text": {
                            "query": query,
                            "path": "article_title",
                            "score": {
                                "boost": {
                                    "value": 2
                                }
                            },
                        }
                    },
                ],
            },
        }
    },
    {
        "$limit": 5
    },
    {
        "$project": {
            "_id": 0,
            "article_id": 1,
            "article_title": 1,
            "article_slug": 1,
            "content": 1,
            "article_status": 1,
            "score": {
                "$meta": "searchScore"
            },
        }
    },
]

results = list(
    article_chunks_collection.aggregate(
        pipeline
    )
)

print("RESULT COUNT:", len(results))

for result in results:
    print(result)