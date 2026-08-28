# M2 validation record

This record distinguishes completed local verification from the remaining
authenticated browser work. It must be updated after that final journey; it is
not a claim that the entire milestone is signed off.

## Implemented frontend integration

- Dynamic Knowledge Base article list and article detail.
- Admin-only article authoring, editing, version-aware status display,
  publishing, and backend chunk preview.
- Admin-only file ingestion with job progress and document-level failures.
- Admin-only Knowledge Base gap view.
- Authenticated self-help semantic search for all roles.
- Dynamic Suggested Articles during ticket creation. This uses the backend
  retrieval endpoint and does not delay ticket submission.
- Ticket creation now sends the entered `affected_system` field to the
  backend.
- Existing agent Resolution Panel is retained, including draft review, cited
  steps, refusal state, accept, edit-send, reject, and feedback.

## API and authorization coverage

- `GET /api/knowledge/articles/{id}/` supplies article detail to authenticated
  users. Non-admin users receive only published, non-internal articles.
- Non-admin article lists now exclude `is_internal_only` articles, preventing
  metadata enumeration.
- `POST /api/knowledge/ingest-upload/` is an Admin-only browser upload adapter
  around the existing ingestion pipeline. It stages only the submitted files
  and returns original file names rather than temporary server paths.
- The client normalizes both `_id` (create response) and `id` (list/detail
  response) so a newly created draft can be previewed and published.

## Commands and observed results

| Check | Result |
| --- | --- |
| `client: npx eslint src/components/knowledge-base/KnowledgeBasePage.tsx src/components/knowledge-base/SuggestedArticles.tsx src/services/knowledgeBaseService.ts` | Passed |
| `client: npm run typecheck` | Passed |
| `client: npm run build` | Passed |
| `server: manage.py test apps.knowledge_base.test_views apps.tickets.test_resolution_views --verbosity 2` | Passed: 16 tests |
| Local unauthenticated `GET /api/knowledge/articles/` | Passed: 401 with `Authorization header missing.` |
| Local browser landing/sign-in navigation | Passed; no browser console errors observed |
| Local browser authentication origin | Fixed and verified: `http://127.0.0.1:5173` is now permitted by backend CORS |
| Local Agent queue browser journey | Passed: 34 active queue rows render with no HTTP 500 or browser console errors |

The full Django-discovered suite was requested but not run because the local
permission control rejected that execution. It remains required before final
sign-off.

## Remaining sign-off checks

An existing test account for each role is required for these real browser
journeys:

1. Admin: create/edit a disposable KB article, preview chunks, publish it,
   upload a disposable document, and inspect ingestion/gaps/search.
2. Agent: open a real ticket, generate a resolution, verify the draft/citation
   state, then edit and send or accept it; submit feedback.
3. Requester: verify self-help and Suggested Articles expose only external
   published knowledge, including a refusal/insufficient-context case.

Those steps intentionally create or update application records and therefore
must be performed with designated disposable test data.

## Queue regression fixed

The queue endpoint was returning raw MongoDB ticket documents. An active
ticket's internal `latest_response_id` ObjectId could not be JSON serialized,
which made `GET /api/tickets/queue/` return HTTP 500. The endpoint now uses
the existing `EmployeeTicketSerializer`, matching the other ticket responses
and excluding internal database references. The focused queue test and a live
Agent browser check both pass.
