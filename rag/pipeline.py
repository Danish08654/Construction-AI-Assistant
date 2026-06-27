import os
import json
from typing import Optional

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()


# =========================================================
# SYSTEM PROMPT
# =========================================================
CONSTRUCTION_SYSTEM_PROMPT = """
You are an expert AI assistant specializing in construction, building codes,
permits, structural engineering, materials, and cost estimation.

Use the provided context to answer questions clearly and practically.

Context:
{context}

Question:
{question}

Answer:
"""


# =========================================================
# RAG CLASS
# =========================================================
class ConstructionRAG:
    """
    Production-grade RAG pipeline for construction domain.
    """

    def __init__(self, index_path: str = None):

        # -------------------------------------------------
        # FIX: ABSOLUTE PATH (CRITICAL FIX)
        # -------------------------------------------------
        BASE_DIR = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )

        self.index_path = index_path or os.path.join(
            BASE_DIR,
            "knowledge_base",
            "index"
        )

        self.embeddings = None
        self.vectorstore = None
        self.llm = None
        self.chain = None
        self._initialized = False

    # =====================================================
    # INITIALIZE PIPELINE
    # =====================================================
    def initialize(self):

        if self._initialized:
            return

        print("\n🚀 Initializing Construction RAG pipeline...")

        # -------------------------------------------------
        # DEBUG PATH CHECK (IMPORTANT)
        # -------------------------------------------------
        print(f"📂 Index Path: {self.index_path}")
        print(f"📂 Exists: {os.path.exists(self.index_path)}")

        if not os.path.exists(self.index_path):
            raise FileNotFoundError(
                f"FAISS index not found at {self.index_path}. "
                "Run builder.py first."
            )

        # -------------------------------------------------
        # EMBEDDINGS
        # -------------------------------------------------
        print("🔄 Loading embeddings model...")

        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )

        # -------------------------------------------------
        # LOAD FAISS INDEX
        # -------------------------------------------------
        print("📦 Loading FAISS index...")

        self.vectorstore = FAISS.load_local(
            self.index_path,
            self.embeddings,
            allow_dangerous_deserialization=True
        )

        # -------------------------------------------------
        # LLM (GROQ)
        # -------------------------------------------------
        print("🤖 Initializing Groq LLM...")

        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            api_key=os.getenv("GROQ_API_KEY"),
            max_tokens=1500
        )

        # -------------------------------------------------
        # RETRIEVER
        # -------------------------------------------------
        retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )

        # -------------------------------------------------
        # FORMAT DOCS
        # -------------------------------------------------
        def format_docs(docs):
            return "\n\n---\n\n".join(
                f"[{doc.metadata.get('title', 'Unknown')}]\n{doc.page_content}"
                for doc in docs
            )

        # -------------------------------------------------
        # PROMPT + CHAIN
        # -------------------------------------------------
        prompt = ChatPromptTemplate.from_template(
            CONSTRUCTION_SYSTEM_PROMPT
        )

        self.chain = (
            {
                "context": retriever | format_docs,
                "question": RunnablePassthrough()
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )

        self._initialized = True

        print("✅ Construction RAG pipeline ready.\n")

    # =====================================================
    # QUERY
    # =====================================================
    def query(self, question: str) -> dict:

        if not self._initialized:
            self.initialize()

        answer = self.chain.invoke(question)

        retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": 5}
        )

        source_docs = retriever.invoke(question)

        return {
            "answer": answer,
            "sources": list({
                doc.metadata.get("title", "Unknown")
                for doc in source_docs
            }),
            "categories": list({
                doc.metadata.get("category", "general")
                for doc in source_docs
            }),
            "chunks_used": len(source_docs)
        }

    # =====================================================
    # SIMILARITY SEARCH
    # =====================================================
    def similarity_search(self, query: str, k: int = 5):

        if not self._initialized:
            self.initialize()

        docs = self.vectorstore.similarity_search(query, k=k)

        return [
            {
                "content": doc.page_content[:300],
                "title": doc.metadata.get("title"),
                "category": doc.metadata.get("category")
            }
            for doc in docs
        ]


# =========================================================
# SINGLETON INSTANCE
# =========================================================
_rag_instance: Optional[ConstructionRAG] = None


def get_rag() -> ConstructionRAG:
    global _rag_instance

    if _rag_instance is None:
        _rag_instance = ConstructionRAG()
        _rag_instance.initialize()

    return _rag_instance