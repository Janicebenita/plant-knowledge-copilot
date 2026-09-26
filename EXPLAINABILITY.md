# Plant Knowledge Copilot Explainability

## Decision and Reasoning Process

The agent's decision process starts by converting the user's question into a MiniLM embedding and comparing it with indexed document chunks using cosine similarity. It accepts only passages that meet the configured relevance threshold, supplies those passages as quoted evidence to the generation model, and requires the answer to remain within that evidence.

If no retrieved passage qualifies, the agent decides that the available knowledge base does not support the requested answer and declines to speculate. Retrieved document text is treated as data rather than instructions, which prevents embedded document prompts from changing the agent's reasoning rules.

## Inputs and Data Sources Used

The primary inputs are the user's question and plant documents indexed from TXT, Markdown, text-based PDF, DOCX, or saved HTML files. The data sources may include maintenance records, procedures, manuals, and other authorized plant documents, with filename, page number where applicable, document hash, and chunk index retained as metadata.

The repository's bundled demonstration documents are explicitly synthetic and are used only to show system behaviour. Optional MongoDB data is limited to conversation history and is not a substitute for the persistent Chroma knowledge base.

## Outputs and Source Evidence

The agent outputs a concise answer with numbered citations such as [1] and [2]. Each citation links the answer to an exact retrieved excerpt and displays its source filename and PDF page when page metadata exists.

A citation demonstrates which passage supported the response, but it does not independently prove that the underlying document is current or correct. Users can inspect the excerpts and compare the answer with the approved source document before relying on it.

## Limits, Constraints, and Known Issues

A central limitation is that the agent can answer only from documents successfully extracted, indexed, and retrieved above the configured similarity threshold. Scanned or image-only PDFs require OCR before ingestion, private records require appropriate access controls, and retrieval settings must be recalibrated for each real plant corpus.

Another known issue is that language-model interpretation can still be incomplete or incorrect even when citations are present. The system has no production control, execution, approval, or maintenance-action capability and must not replace plant procedures, safety systems, document-control requirements, or qualified engineering judgement.

## Uncertainty and Human Review

The agent reports insufficient evidence when retrieval does not meet the acceptance threshold and avoids converting weak similarity into a confident response. It also identifies synthetic data, missing page information, incomplete records, and other conditions that reduce confidence.

All operationally important answers require human review against the latest approved source documents and current field conditions. Authorized personnel remain responsible for deciding whether to inspect equipment, isolate systems, perform maintenance, change operating conditions, or return equipment to service.

