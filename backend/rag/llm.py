from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from core.config import settings

SYSTEM_PROMPT = """You are DocMind, a Q&A assistant that answers questions based on provided context.

CRITICAL RULES:
1. The user has asked a question — ALWAYS answer it. Never say "no question was provided" or similar.
2. Search the ENTIRE context below for relevant information before responding.
3. If the answer exists ANYWHERE in the context — even embedded in a longer passage — provide it with citations [1], [2], etc.
4. Answer ONLY the specific question asked. Do not generate extra Q&A or follow-up questions.
5. Keep answers concise and direct. No preamble, no restating the question.
6. If the answer is truly not in the context, say: "I couldn't find this in the uploaded documents."
7. Never invent information not present in the context."""

HUMAN_PROMPT = """A user has asked the following question. Use the context below to answer it.

--- CONTEXT ---
{context}
--- END CONTEXT ---

USER'S QUESTION: {question}

Answer the user's question using the context above. If the context contains relevant information, cite it with [1], [2], etc."""


def build_context(sources: list[dict]) -> str:
    parts = []
    for i, src in enumerate(sources, 1):
        parts.append(f'[{i}] (page {src["page"]}) "{src["text"]}"')
    return "\n".join(parts)


def get_llm():
    return ChatGroq(
        model=settings.llm_model,
        api_key=settings.groq_api_key,
        streaming=True,
        temperature=0.1,
        max_tokens=1024,
    )


def build_messages(question: str, sources: list[dict]) -> list:
    context = build_context(sources)
    prompt = HUMAN_PROMPT.format(context=context, question=question)
    return [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)]
