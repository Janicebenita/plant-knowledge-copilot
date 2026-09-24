# Architecture

```mermaid
flowchart LR
  U["TXT / Markdown / PDF / DOCX / HTML"] --> X["Extract + clean"]
  X --> C["Boundary-aware chunks + source metadata"]
  C --> E["all-MiniLM-L6-v2 embeddings"]
  E --> V["Persistent Chroma / cosine"]
  Q["Question"] --> R["Thresholded retrieval"]
  V --> R
  R --> G["Groq active Llama model"]
  G --> A["Answer + numbered evidence"]
  A --> M["MongoDB history when configured"]
```

Trust boundaries: uploads and retrieved text are untrusted data. The system prompt prohibits following instructions found in retrieved text. Chroma collection metadata pins the embedding model and cosine distance; startup refuses a conflicting existing collection.

