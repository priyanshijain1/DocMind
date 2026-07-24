from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    answer_relevancy,
    context_precision,
    context_recall,
    faithfulness,
)

from rag.llm import build_messages, get_llm
from rag.retrieval import hybrid_search


def build_qa_pairs(test_data: list[dict], user_id: str) -> list[dict]:
    llm = get_llm()
    results = []

    for item in test_data:
        question = item["question"]
        ground_truth = item["ground_truth"]

        sources = hybrid_search(question, user_id=user_id, top_k=10)
        context_texts = [s["text"] for s in sources]

        messages = build_messages(question, sources)
        response = llm.invoke(messages)
        answer = response.content

        results.append(
            {
                "question": question,
                "answer": answer,
                "contexts": context_texts,
                "ground_truth": ground_truth,
            }
        )

    return results


def run_evaluation(test_data: list[dict], user_id: str = "anonymous") -> dict:
    qa_pairs = build_qa_pairs(test_data, user_id)
    dataset = Dataset.from_list(qa_pairs)

    result = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
    )

    return {
        "faithfulness": result["faithfulness"],
        "answer_relevancy": result["answer_relevancy"],
        "context_precision": result["context_precision"],
        "context_recall": result["context_recall"],
        "num_samples": len(qa_pairs),
    }
