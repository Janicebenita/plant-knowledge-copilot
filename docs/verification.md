# Verification record

Verified locally on 2026-09-24 with Python 3.12:

- `ruff check .` — passed.
- `pytest` — 12 tests passed.
- Real `sentence-transformers/all-MiniLM-L6-v2` embeddings loaded successfully.
- Four bundled synthetic files indexed into persistent Chroma and a Pump P-101 query retrieved the expected source first.
- Retrieval evaluation — 3/3 passed at the documented 0.50 cosine-similarity threshold. This is a retrieval result, not an answer-quality claim.
- Streamlit `/_stcore/health` — HTTP 200 `ok`.
- Browser rendering — meaningful page content, expected upload/chunk/index/new-conversation/chat controls, and no framework error overlay.
- UI bundled-example indexing — passed.
- UI query with no Groq credential — reached retrieval and displayed the explicit missing-key error.

Not verified:

- Groq generation, because no `GROQ_API_KEY` was available. No answer-quality claim is made.
- MongoDB persistence, because no `MONGODB_URI` was available. The UI correctly labeled history as session-only.
- Scanned PDF OCR, which is intentionally not implemented; scanned PDFs require preprocessing with OCR.

Groq model note: public Groq documentation at verification time marked the previously common general-purpose Llama IDs as deprecated. The project therefore requires `GROQ_MODEL` to be selected from the authenticated account's active Models API response and validates it before generation instead of shipping a stale default.

