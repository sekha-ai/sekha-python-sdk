# Emergency Endpoint Restoration - Feb 9, 2026

## 🚨 Critical Issue Discovered

While developing the Python SDK, discovered that PR #27 (v2.0 provider registry merge) **deleted 10 functional endpoints** from the controller during merge on Feb 8, 2026.

## Root Cause Analysis

### Before Merge (commit f09a150be)
- ✅ **19 fully functional endpoints** in `routes.rs`
- ✅ All endpoints documented and working
- ✅ Complete API coverage

### After Merge (commit 4d1abe8)
- ❌ **Only 9 endpoints remained**
- ❌ 10 endpoints completely deleted
- ❌ Python SDK would fail on documented endpoints

### Merge Statistics
- **344 commits** merged
- **72 files changed**
- **15,320 additions, 4,221 deletions**
- Routes.rs was completely rewritten, losing critical code

## Restoration Actions

### Controller Fixes (sekha-controller)

**Commit:** [07fcff9](https://github.com/sekha-ai/sekha-controller/commit/07fcff9d92b3e99a4c0e18b9572c13836bfbaf3d)

Restored all 10 missing endpoints to `src/api/routes.rs`:

#### Conversation Management (3 restored)
1. `PUT /api/v1/conversations/{id}/folder` - Update folder
2. `PUT /api/v1/conversations/{id}/pin` - Pin conversation
3. `PUT /api/v1/conversations/{id}/archive` - Archive conversation

#### Search Operations (2 restored)
4. `POST /api/v1/search/fts` - Full-text search (SQLite FTS5)
5. `POST /api/v1/rebuild-embeddings` - Trigger embedding rebuild

#### Memory Orchestration (5 restored)
6. `POST /api/v1/context/assemble` - Intelligent context assembly
7. `POST /api/v1/summarize` - Generate hierarchical summaries
8. `POST /api/v1/prune/dry-run` - Get pruning suggestions
9. `POST /api/v1/prune/execute` - Execute pruning (archive)
10. `POST /api/v1/labels/suggest` - AI-powered label suggestions

### Python SDK Fixes (sekha-python-sdk)

**Commits:**
- [a823452](https://github.com/sekha-ai/sekha-python-sdk/commit/a823452256a08ababda97c7ed734a92b69da2da6) - Client fixes
- [1b7883d](https://github.com/sekha-ai/sekha-python-sdk/commit/1b7883d0e8688a0e4b1be4318484e34cbbe99ee7) - Model fixes
- [93f493f](https://github.com/sekha-ai/sekha-python-sdk/commit/93f493f40bec62c833d5cd7ad58c17411021c2f8) - Test coverage

#### Changes to `sekha/client.py`

**Removed (phantom endpoints):**
- `score_message_importance()` - Endpoint never existed
- `generate_summary()` - Wrong signature/path
- `get_pruning_suggestions()` - Wrong path
- `get_mcp_tools()` - MCP routes not mounted
- `export()` - Endpoint doesn't exist
- `_update_status()` - Generic status update doesn't exist
- `pin()` - Wrong endpoint (now `pin_conversation()`)
- `archive()` - Wrong endpoint (now `archive_conversation()`)

**Added (correct implementations):**
- `update_folder()` - PUT /api/v1/conversations/{id}/folder
- `pin_conversation()` - PUT /api/v1/conversations/{id}/pin
- `archive_conversation()` - PUT /api/v1/conversations/{id}/archive
- `count_conversations()` - GET /api/v1/conversations/count
- `full_text_search()` - POST /api/v1/search/fts
- `rebuild_embeddings()` - POST /api/v1/rebuild-embeddings
- `assemble_context()` - POST /api/v1/context/assemble
- `summarize()` - POST /api/v1/summarize
- `prune_dry_run()` - POST /api/v1/prune/dry-run
- `prune_execute()` - POST /api/v1/prune/execute
- `suggest_labels()` - POST /api/v1/labels/suggest

**Fixed:**
- Changed `/api/v1/query/smart` → `/api/v1/query` (correct path)
- Fixed wildcard imports (`from .models import *` → explicit imports)
- Fixed `asyncio.run()` issue in `SyncSekhaClient`
- Added `offset` parameter to `query()` method
- Fixed `list_conversations()` to return `QueryResponse` not `List[ConversationResponse]`

#### Changes to `sekha/models.py`

**Added:**
- `ClientConfig` dataclass (was missing entirely)
- `offset` field to `QueryRequest`

**Fixed:**
- `ConversationResponse.status` changed from enum to string (matches controller)
- `QueryRequest` now matches controller DTO exactly
- `SummaryResponse` structure matches controller response
- `HealthResponse` matches actual controller health check format

## Complete Endpoint Coverage

### ✅ All 19 Controller Endpoints Now Mapped

#### Conversations (9)
1. POST `/api/v1/conversations` - Create
2. GET `/api/v1/conversations/{id}` - Read
3. GET `/api/v1/conversations` - List
4. PUT `/api/v1/conversations/{id}/label` - Update label
5. PUT `/api/v1/conversations/{id}/folder` - Update folder ✨ **RESTORED**
6. PUT `/api/v1/conversations/{id}/pin` - Pin ✨ **RESTORED**
7. PUT `/api/v1/conversations/{id}/archive` - Archive ✨ **RESTORED**
8. DELETE `/api/v1/conversations/{id}` - Delete
9. GET `/api/v1/conversations/count` - Count

#### Search & Query (3)
10. POST `/api/v1/query` - Semantic search
11. POST `/api/v1/search/fts` - Full-text search ✨ **RESTORED**
12. POST `/api/v1/rebuild-embeddings` - Rebuild embeddings ✨ **RESTORED**

#### Memory Orchestration (5)
13. POST `/api/v1/context/assemble` - Assemble context ✨ **RESTORED**
14. POST `/api/v1/summarize` - Generate summary ✨ **RESTORED**
15. POST `/api/v1/prune/dry-run` - Pruning suggestions ✨ **RESTORED**
16. POST `/api/v1/prune/execute` - Execute pruning ✨ **RESTORED**
17. POST `/api/v1/labels/suggest` - Suggest labels ✨ **RESTORED**

#### Health & Metrics (2)
18. GET `/health` - Health check
19. GET `/metrics` - Metrics

## Testing

Created comprehensive test suite: `tests/test_all_endpoints.py`
- Tests all 19 endpoints
- Validates request/response formats
- Ensures no 404s on documented endpoints
- Provides endpoint coverage report

## Impact Assessment

### What This Prevented
- ❌ **Show HN embarrassment** - SDK claiming features that don't exist
- ❌ **User frustration** - Documented endpoints returning 404
- ❌ **Lost credibility** - "Vaporware" accusations
- ❌ **Wasted user time** - Debugging non-existent endpoints

### Lessons Learned
1. **Never trust large merges** - 344 commits is catastrophic
2. **Always audit after merge** - Especially massive refactors
3. **Test SDK against live API** - Would've caught this immediately
4. **Endpoint-level integration tests** - Should be automated
5. **OpenAPI spec validation** - Would prevent endpoint drift

## Next Steps

### Immediate (Done ✅)
- [x] Restore all 10 missing endpoints in controller
- [x] Fix Python SDK to match controller exactly
- [x] Add comprehensive endpoint tests
- [x] Document all fixes

### Short-term
- [ ] Add OpenAPI/Swagger spec generation
- [ ] Create automated endpoint validation
- [ ] Add integration test CI pipeline
- [ ] Generate SDK from OpenAPI spec

### Long-term
- [ ] Contract testing with Pact
- [ ] Automated API changelog generation
- [ ] SDK auto-generation pipeline
- [ ] Endpoint deprecation workflow

## Conclusion

This was a near-catastrophic failure caught just in time. The v2.0 merge deleted 52% of the API surface area without anyone noticing. Only discovered due to SDK development forcing us to actually call the documented endpoints.

**Critical takeaway:** Documentation and code can diverge silently. Always validate.

---

*Fixed by: AI Assistant + @jefftraylor*  
*Date: February 9-10, 2026*  
*Time to detect: 2 months (Dec 9 → Feb 9)*  
*Time to fix: 1 hour*
