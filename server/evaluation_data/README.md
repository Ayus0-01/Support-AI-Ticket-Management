# M2 Evaluation Data

## retrieval_candidates.json

This file is generated from the live MongoDB ticket corpus and the
currently published Knowledge Base.

The candidate articles are NOT ground truth.

For each candidate case:

1. Review the ticket.
2. Review the candidate articles.
3. Identify the article(s) that genuinely answer the ticket.
4. Put their MongoDB article IDs into `expected_article_ids`.
5. Change `review_status` to `REVIEWED`.

Only reviewed cases should be copied into:

`retrieval_golden.json`

## Retrieval evaluation

The frozen retrieval set should contain 100 curated
ticket -> article pairs.

Metrics:

- Recall@1
- Recall@5
- MRR
- Mean rerank score

M2 Recall@5 target:

>= 0.85

Do not derive `expected_article_ids` from the retriever output.
The retrieval system must never be allowed to define its own
ground truth.