# Plant Knowledge Copilot

A citation-first RAG application for searching plant documents. It indexes TXT, Markdown, text-based PDF, DOCX, and saved HTML; retrieves relevant passages from persistent Chroma; and asks Groq to answer only from those passages.

> **Safety:** bundled records are clearly marked **SYNTHETIC** and are not verified industrial guidance. This tool does not authorize maintenance or replace approved procedures, engineering review, or qualified personnel.

## What it does

- Extracts readable text, strips scripts/styles/navigation from HTML, normalizes whitespace, rejects empty/unsupported/malformed files, and explains that scanned PDFs need OCR.
- Splits at paragraph/sentence boundaries with configurable size and overlap. Filename and 1-based PDF page number remain on every chunk.
- Embeds with `sentence-transformers/all-MiniLM-L6-v2` and persists in Chroma with cosine distance.
- Uses a SHA-256 document hash for idempotency; re-uploading an unchanged filename is a no-op, while changed content replaces that filename's old chunks.
- Refuses an existing collection whose embedding-model or distance metadata differs, preventing silent vector incompatibility.
- Applies a cosine-similarity threshold (`0.50` by default, calibrated against the bundled retrieval set), shows numbered exact excerpts, and returns an explicit unsupported answer when retrieval finds no qualifying evidence.
- Treats retrieved content as untrusted data rather than instructions.
- Stores history in MongoDB when configured; otherwise the UI explicitly says history is session-only.

See [the architecture diagram](docs/architecture.md).
See [the implementation verification record](docs/verification.md) for the exact tested scope.

## Local setup

Python 3.11 is recommended.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
copy .env.example .env  # Windows; use: cp .env.example .env
```

Set `GROQ_API_KEY` and `GROQ_MODEL` in `.env`. Model availability changes: use the Groq Models API for your account and choose an **active generative Llama** ID. The application validates availability at request time and fails clearly rather than silently using a retired model. As of the repository's publication date, Groq's public documentation showed its former general-purpose Llama IDs as deprecated, so no stale default is committed.

Run:

```bash
streamlit run app.py
```

Upload the files in `demo_data/`, click **Index documents**, then ask: `What vibration was recorded after maintenance on Pump P-101?`

## Tests and evaluation

```bash
pytest
ruff check .
python evaluate.py
```

Tests cover HTML/DOCX extraction and bad uploads, boundary-aware chunking and metadata, idempotent/replacement ingestion, thresholded retrieval, and the no-evidence unsupported response. `evaluate.py` reports **retrieval results only** against expected source filenames. Its `reference_facts` are a reproducible basis for a future human or model-based answer review; the script deliberately makes no answer-quality claim.

## Configuration

All credentials come from environment variables; `.env` is ignored. `CHROMA_PATH`, collection name, embedding model, chunking, `TOP_K`, and `RELEVANCE_THRESHOLD` are explicit in `.env.example`.

MongoDB is optional. Configure `MONGODB_URI` and `MONGODB_DATABASE` for durable history. Uploaded files themselves are not written to disk; extracted chunks are stored in Chroma. Do not index private records into a shared deployment without appropriate access controls and retention policy.

## Deployment

Build the included container and mount a durable volume at the configured `CHROMA_PATH`:

```bash
docker build -t plant-knowledge-copilot .
docker run --rm -p 8501:8501 --env-file .env -e CHROMA_PATH=/data/chroma -v plant-kb:/data plant-knowledge-copilot
```

For a managed container platform:

1. Store `GROQ_API_KEY` and optional `MONGODB_URI` in its secret manager, never the image or repository.
2. Select and configure a currently active account-visible generative Llama model as `GROQ_MODEL`.
3. Attach a persistent filesystem/volume and point `CHROMA_PATH` to it. Many serverless/Streamlit hosts have ephemeral local filesystems: without a volume, the knowledge base disappears on restart or redeploy and multiple replicas will not share vectors.
4. Use a single writer or a shared vector service for multi-replica deployments. Add authentication before exposing private documents.
5. Run health checks against Streamlit's `/_stcore/health` endpoint.

MongoDB only persists conversation messages; it does not make Chroma persistent.

## Limitations

- Scanned/image-only PDFs are not OCR'd; run OCR before upload.
- Password-protected documents and malformed containers are rejected.
- Retrieval relevance is tunable and must be evaluated for the target corpus.
- Citations show the exact retrieved excerpts, not proof that a generated interpretation is correct.
- No live Groq or MongoDB claim should be made unless credentials and connectivity were used in that environment.

## Starter provenance

The supplied `industrial-rag-starter.zip` was inspected before publication. Its extraction, prompt-injection boundary, session-history messaging, synthetic maintenance-policy record, and bundled-example workflow informed this implementation. The code was substantially restructured to add explicit collection compatibility checks, byte-based safe extraction, replacement/idempotency metadata, model-availability validation, stronger tests, deployment artifacts, and separate retrieval evaluation. The starter's retired hard-coded Groq model default was intentionally removed.
