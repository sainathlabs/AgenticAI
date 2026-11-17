# -*- coding: utf-8 -*-
"""
Central prompt library for the MM-RAG project.

Everything the generator and the UI need in terms of wording lives here, so
prompts can be tuned without touching retrieval or Streamlit code.

Consumers:
    src/generation.py -> MULTIMODAL_RAG_SYSTEM_PROMPT,
                         format_multimodal_rag_user_prompt,
                         format_retrieved_image_evidence_prompt,
                         GENERATION_SMOKE_TEST_QUERY
    ui/app.py         -> CHAT_SUGGESTED_PROMPTS
"""

from __future__ import annotations

from typing import Any


__all__ = [
    "MULTIMODAL_RAG_SYSTEM_PROMPT",
    "CHAT_SUGGESTED_PROMPTS",
    "GENERATION_SMOKE_TEST_QUERY",
    "format_multimodal_rag_user_prompt",
    "format_retrieved_image_evidence_prompt",
]


# ---------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------

MULTIMODAL_RAG_SYSTEM_PROMPT = """You are a careful document analyst answering \
questions about one specific document.

You are given two kinds of evidence:
1. Text context blocks retrieved from the document. Each block starts with a
   header containing a `Citation:` value such as `[report.pdf p.12]`, plus the
   file name, page number and content type (text, table or image).
2. Zero or more page images from the document. Each image is introduced by a
   short text note that repeats its citation.

Rules you must follow:
- Answer ONLY from the supplied evidence. Never use outside knowledge and
  never guess at numbers, dates, names or clause wording.
- If the evidence does not contain the answer, say so plainly, state what is
  missing, and suggest what to search for instead. Do not pad the reply.
- Cite the source for every factual claim, using the exact `Citation:` value
  from the evidence, for example `[report.pdf p.12]`. Put the citation right
  after the sentence or table row it supports.
- When the evidence contradicts itself, present both readings with their
  separate citations instead of silently picking one.
- Tables arrive as Markdown. Preserve the real figures, units and row labels;
  quote numbers exactly as written rather than rounding or recomputing them.
- When you rely on a page image (a chart, diagram, scan or photo), describe
  what you actually see in it and cite that image's citation. Do not infer
  values from an image that are not legible.
- Keep the structure practical: a short direct answer first, then supporting
  detail as a brief table or bullets when there is more than one fact.
- Use plain language, and write amounts and dates in the same format the
  document uses.

You are describing what the document says. You are not giving legal, medical
or financial advice.
"""


# ---------------------------------------------------------------------
# User prompt
# ---------------------------------------------------------------------

_MULTIMODAL_RAG_USER_PROMPT_TEMPLATE = """Answer the question using only the \
evidence below.

QUESTION
{query}

RETRIEVED EVIDENCE
{context}

INSTRUCTIONS
- Ground every statement in the evidence above and cite it with the exact
  `Citation:` value shown in the source header.
- If the evidence is insufficient or only partly answers the question, say
  exactly which part is unsupported.
- Prefer a short answer followed by a compact table or bullets for details.
- Any page images supplied after this message are additional evidence for the
  same question; cite them the same way.
"""

_NO_CONTEXT_PLACEHOLDER = (
    "No text context was retrieved for this question."
)


def format_multimodal_rag_user_prompt(
    *,
    query: str,
    context: str,
) -> str:
    """
    Build the main user prompt for a multimodal RAG turn.

    Args:
        query: The user's question, as typed.
        context: The joined retrieved context sections built by
            MultimodalRAGGenerator._prepare_context.

    Returns:
        The formatted user prompt text.
    """
    clean_query = str(query or "").strip()
    clean_context = str(context or "").strip()

    if not clean_context:
        clean_context = _NO_CONTEXT_PLACEHOLDER

    return _MULTIMODAL_RAG_USER_PROMPT_TEMPLATE.format(
        query=clean_query,
        context=clean_context,
    )


# ---------------------------------------------------------------------
# Image evidence prompt
# ---------------------------------------------------------------------

def format_retrieved_image_evidence_prompt(
    *,
    citation: str,
    image_index: Any = None,
) -> str:
    """
    Build the short note that introduces one retrieved page image.

    Args:
        citation: The citation label for the image, e.g. `[report.pdf p.4]`.
        image_index: Optional per-page image number from the parser.

    Returns:
        The text block placed immediately before the image itself.
    """
    clean_citation = str(citation or "").strip() or "[unknown source]"

    if image_index in {None, "", -1, "-1"}:
        label = clean_citation
    else:
        label = f"{clean_citation} (image {image_index})"

    return (
        "IMAGE EVIDENCE\n"
        f"Citation: {label}\n"
        "The next image comes from the document. Read it directly: use the "
        "visible labels, axis values, legends and table cells. Cite it as "
        f"{clean_citation} when you rely on it, and say so plainly if a "
        "value is not legible."
    )


# ---------------------------------------------------------------------
# UI suggestions
# ---------------------------------------------------------------------

CHAT_SUGGESTED_PROMPTS: list[str] = [
    "Summarise this document in 10 bullet points",
    "What are the key dates, deadlines and obligations?",
    "List every table and tell me what each one shows",
    "Explain the charts, diagrams and images in the document",
    "What numbers, amounts or financial figures are stated?",
    "What risks, exclusions or penalties are mentioned?",
]


# ---------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------

GENERATION_SMOKE_TEST_QUERY = (
    "Give a short summary of this document and cite the pages you used."
)
