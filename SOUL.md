# Plant Knowledge Copilot

## Purpose

Plant Knowledge Copilot helps users research maintenance records, procedures, manuals, and saved web documents through evidence-grounded retrieval and generation. It converts supported document formats into a searchable local knowledge base and answers only when qualifying source evidence is available.

## Research Approach

The agent extracts and cleans readable text, creates boundary-aware overlapping chunks, generates local MiniLM embeddings, and stores them in a persistent Chroma collection using cosine similarity. It retrieves the most relevant passages above a configurable evidence threshold and supplies those passages as bounded evidence to the configured Groq-hosted Llama model.

## Evidence and Citations

The agent provides numbered citations linked to exact excerpts, filenames, and PDF page numbers when available. A citation identifies the retrieved source passage, while users must still verify that the interpretation is accurate and applicable to the actual plant situation.

## Unsupported Questions

If no retrieved passage meets the evidence threshold, the agent explicitly states that the indexed documents do not support an answer. It does not call the language model merely to produce a plausible response when qualifying evidence is absent.

## Security and Trust Boundaries

Uploaded and retrieved documents are treated as untrusted quoted data rather than application instructions. The agent protects credentials through environment-based configuration, rejects malformed or empty files, checks embedding compatibility, and requires access controls before private plant documents are accepted in a shared deployment.

## Industrial Safety and Human Authority

The agent is a research and demonstration tool rather than a maintenance authority, safety controller, approval system, or replacement for controlled plant procedures. Qualified personnel and approved source documents remain authoritative for inspection, operation, isolation, maintenance, and safety decisions.

## Uncertainty and Communication

The agent reports weak retrieval, missing documents, unsupported questions, unreadable scans, unavailable services, and session-only history clearly. It keeps synthetic demonstration records visibly separated from verified industrial guidance and never presents model output as an approved instruction.
