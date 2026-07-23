from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from core.config import settings

PROMPT_TEMPLATE = """You are DocMind, an AI assistant that answers questions strictly
based on the provided context. Always cite your sources using [1], [2], etc.
If the answer is not found in the context, say:
"I couldn't find this in the uploaded documents." — do not guess.

---
Context (retrieved passages):
{context}
---

Question: {question}

Answer:"""


def build_context(sources: list[dict]) -> str:
    parts = []
    for i, src in enumerate(sources, 1):
        parts.append(f'[{i}] (page {src["page"]}, doc: {src["doc_id"]}) "{src["text"]}"')
    return "\n".join(parts)


def get_llm():
    return ChatGroq(
        model=settings.llm_model,
        api_key=settings.groq_api_key,
        streaming=True,
    )


def build_messages(question: str, sources: list[dict]) -> list:
    context = build_context(sources)
    prompt = PROMPT_TEMPLATE.format(context=context, question=question)
    return [SystemMessage(content="You are DocMind."), HumanMessage(content=prompt)]
