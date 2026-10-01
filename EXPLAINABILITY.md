# Plant Knowledge Copilot Explainability

## Decision and Reasoning Process

The agent's decision process extracts and validates readable text, divides it into paragraph- or sentence-aware chunks, creates local MiniLM embeddings, and searches the Chroma collection using cosine similarity. Its reasoning accepts only passages meeting the configured relevance threshold and declines the question without a language-model call when no qualifying evidence is found.

When evidence is available, the agent provides the retrieved excerpts to the configured generative Llama model as delimited reference data rather than instructions. The generated response must remain grounded in those excerpts and use numbered citations that users can expand and inspect.

## Inputs and Data Sources Used

Input data may include authorized TXT, Markdown, text-based PDF, DOCX, and saved HTML documents. Extraction preserves filenames and, for PDFs, one-based page numbers together with document hashes, chunk indexes, and embedding-model identifiers.

The bundled demonstration corpus contains clearly marked synthetic maintenance and procedure records and must not be treated as verified plant guidance. Optional MongoDB stores conversation history when configured, while the Chroma collection stores the searchable document vectors and metadata.

## Outputs and Supporting Evidence

The agent outputs an evidence-grounded answer with numbered citations and expandable exact source excerpts. Supporting evidence includes the retrieved text, filename, PDF page where available, similarity qualification, source hash, and chunk metadata.

If supporting evidence is insufficient, the output is an explicit unsupported-answer message rather than a speculative response. Conversation history is labelled as durable only when MongoDB is configured; otherwise, it remains session-only.

## Limits, Constraints, and Known Issues

A principal limitation is that retrieval quality depends on corpus completeness, document quality, chunking, embedding suitability, and threshold calibration. Known constraints include the need for external OCR for scanned PDFs, possible retrieval errors, model-generation errors, changing hosted-model availability, and loss of local Chroma data when deployed without persistent storage.

A citation proves which passage was retrieved but does not prove that the source is correct, current, approved, or properly interpreted. The agent cannot execute plant actions, approve work, control equipment, replace document-control systems, or determine whether a procedure applies safely to a specific field condition.

## Uncertainty and Human Review

Uncertainty is reported when passages are weakly related, multiple sources conflict, metadata is incomplete, model services are unavailable, or the indexed collection lacks necessary information. Users should treat low-context answers, synthetic records, and unverified uploads with particular caution.

Human review is mandatory before using an answer for maintenance, operation, safety, compliance, isolation, or engineering decisions. Users must compare citations with the complete approved document, current revision, equipment identity, site conditions, and applicable permit or procedure.

## Safety, Security, and Responsible Use

Retrieved documents are treated as untrusted content so embedded instructions cannot override the application rules or system prompt. Secrets, uploaded private documents, local vector data, model caches, and conversation records must be protected using appropriate authorization, retention, backup, and deletion controls.

The agent must not be connected directly to industrial controls or used as the sole basis for a safety-critical action. Production deployment would require authentication, document-level authorization, audit logging, validated corpora, persistent storage, monitoring, security review, and accountable human ownership.
