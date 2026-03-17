from pathlib import Path

from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import RetrievalQA


PROJECT_ROOT = Path(__file__).resolve().parents[2]
VECTORSTORE_DIR = PROJECT_ROOT / "data" / "vectorstore"


def get_qa_chain() -> RetrievalQA:
    """Return a simple RetrievalQA chain over the persisted Chroma store."""
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma(
        embedding_function=embeddings,
        persist_directory=str(VECTORSTORE_DIR),
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    llm = ChatOpenAI(model="gpt-4o-mini")

    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        verbose=False,
    )


def answer_question(question: str) -> str:
    """Run a basic RAG Q&A over the Berlin corpus."""
    chain = get_qa_chain()
    result = chain.invoke({"query": question})
    return result["result"]


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: uv run python -m planmyberlin.rag.retrieval \"Your question here\"")
        raise SystemExit(1)

    q = " ".join(sys.argv[1:])
    print(answer_question(q))

