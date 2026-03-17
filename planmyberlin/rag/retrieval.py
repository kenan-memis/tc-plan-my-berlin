from pathlib import Path

from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


PROJECT_ROOT = Path(__file__).resolve().parents[2]
VECTORSTORE_DIR = PROJECT_ROOT / "data" / "vectorstore"


def answer_question(question: str) -> str:
    """Run a basic RAG Q&A over the Berlin corpus."""
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma(
        embedding_function=embeddings,
        persist_directory=str(VECTORSTORE_DIR),
    )

    # Retrieve top-k relevant chunks
    docs = vectorstore.similarity_search(question, k=5)
    context = "\n\n---\n\n".join(doc.page_content for doc in docs)

    prompt = (
        "You are a helpful Berlin trip planning assistant.\n"
        "Use the following context about Berlin's neighbourhoods, sights, restaurants, "
        "and transport to answer the user's question. If something is not covered, "
        "be honest about the limits of your knowledge.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Answer:"
    )

    llm = ChatOpenAI(model="gpt-4o-mini")
    response = llm.invoke(prompt)
    return response.content


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: uv run python -m planmyberlin.rag.retrieval \"Your question here\"")
        raise SystemExit(1)

    q = " ".join(sys.argv[1:])
    print(answer_question(q))

