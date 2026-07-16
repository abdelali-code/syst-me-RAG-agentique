"""
Ingestion & vectorisation pipeline for the Agentic RAG Juridique project.

Pipeline:
  1. Load raw documents (.txt, .pdf) from data/raw/
  2. Split into overlapping chunks (article-aware for legal text)
  3. Embed chunks with a local multilingual embedding model
  4. Persist chunks + embeddings + metadata into a DuckDB database
     (data/processed/legal.duckdb)

Design choices (documented for the report):
  - Embeddings run LOCALLY (sentence-transformers / multilingual-e5-base) because
    the xAI Grok API does not expose a public embeddings endpoint (confirmed July 2026).
    This also avoids sending the legal corpus to a third-party embedding API.
  - Chunking is "article-aware": for our legal corpus, splitting on "Article N"
    boundaries keeps each chunk legally coherent (a chunk should not cut an
    article in half), then a RecursiveCharacterTextSplitter handles any
    oversized articles.
  - Vector store: DuckDB (single embedded file, no server to run). Similarity
    search uses DuckDB's built-in `array_cosine_distance` function, which is
    part of core DuckDB and needs no extension download -- important since
    the VSS extension (for an HNSW index) requires internet access to
    extensions.duckdb.org, which may be blocked in locked-down environments.
    Storing `law` / `article` as normal SQL columns alongside the embedding
    also lets `get_article_by_number` do an exact, indexed lookup with plain
    SQL instead of an approximate vector search -- a real advantage of using
    a relational engine as the vector store for structured legal text.
"""
import os
import re
import glob
from pathlib import Path

import duckdb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "legal.duckdb"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-base")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "768"))  # multilingual-e5-base hidden size

ARTICLE_SPLIT_RE = re.compile(r"(?=^Article\s+\S+)", re.MULTILINE)

_embedder = None


def get_embedder() -> HuggingFaceEmbeddings:
    global _embedder
    if _embedder is None:
        _embedder = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embedder


def load_raw_documents() -> list[Document]:
    """Load every .txt and .pdf file under data/raw/ into LangChain Documents."""
    docs: list[Document] = []
    for path in glob.glob(str(RAW_DIR / "*")):
        p = Path(path)
        if p.suffix == ".txt":
            text = p.read_text(encoding="utf-8")
            docs.append(Document(page_content=text, metadata={"source": p.name}))
        elif p.suffix == ".pdf":
            loader = PyPDFLoader(str(p))
            for page in loader.load():
                page.metadata["source"] = p.name
                docs.append(page)
    return docs


def article_aware_chunks(doc: Document) -> list[Document]:
    """Split a legal document on 'Article N' boundaries first, so no chunk
    straddles two articles unless a single article is itself very long."""
    source = doc.metadata.get("source", "unknown")
    header = doc.page_content.strip().split("\n")[0][:120]

    parts = ARTICLE_SPLIT_RE.split(doc.page_content)
    parts = [p for p in parts if p.strip()]
    if len(parts) <= 1:
        return [doc]

    chunks = []
    for part in parts:
        article_match = re.match(r"Article\s+(\S+)", part.strip())
        article_no = article_match.group(1).rstrip(".") if article_match else None
        chunks.append(
            Document(
                page_content=part.strip(),
                metadata={"source": source, "law": header, "article": article_no},
            )
        )
    return chunks


def get_connection(read_only: bool = False) -> duckdb.DuckDBPyConnection:
    """Open a DuckDB connection to the persisted legal database, loading the
    VSS extension for HNSW indexing if it's available (optional, purely a
    speed optimisation -- similarity search works without it via
    array_cosine_distance)."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB_PATH), read_only=read_only)
    try:
        con.execute("INSTALL vss; LOAD vss;")
        con.execute("SET hnsw_enable_experimental_persistence = true;")
    except Exception:
        # No internet access to extensions.duckdb.org, or already loaded --
        # brute-force cosine distance still works fine at this corpus size.
        pass
    return con


def build_vectorstore(persist: bool = True) -> None:
    raw_docs = load_raw_documents()
    if not raw_docs:
        raise RuntimeError(f"No documents found in {RAW_DIR}. Add .txt/.pdf legal texts first.")

    article_chunks: list[Document] = []
    for d in raw_docs:
        article_chunks.extend(article_aware_chunks(d))

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=150,
        separators=["\n\n", "\n", ". ", " "],
    )
    final_chunks = splitter.split_documents(article_chunks)

    print(f"[ingest] Loaded {len(raw_docs)} raw documents -> "
          f"{len(article_chunks)} article-level chunks -> "
          f"{len(final_chunks)} final chunks")

    embedder = get_embedder()
    vectors = embedder.embed_documents([c.page_content for c in final_chunks])
    if vectors:
        actual_dim = len(vectors[0])
        if actual_dim != EMBEDDING_DIM:
            raise RuntimeError(
                f"Embedding dimension mismatch: model produced {actual_dim}-d vectors "
                f"but EMBEDDING_DIM={EMBEDDING_DIM}. Update your .env EMBEDDING_DIM."
            )

    con = get_connection()
    con.execute(f"""
        CREATE OR REPLACE TABLE chunks (
            id INTEGER PRIMARY KEY,
            source VARCHAR,
            law VARCHAR,
            article VARCHAR,
            content VARCHAR,
            embedding FLOAT[{EMBEDDING_DIM}]
        )
    """)
    con.executemany(
        "INSERT INTO chunks VALUES (?, ?, ?, ?, ?, ?)",
        [
            (i, c.metadata.get("source"), c.metadata.get("law"), c.metadata.get("article"),
             c.page_content, vec)
            for i, (c, vec) in enumerate(zip(final_chunks, vectors))
        ],
    )

    try:
        con.execute(
            "CREATE INDEX idx_chunks_embedding ON chunks USING HNSW (embedding) "
            "WITH (metric = 'cosine')"
        )
        print("[ingest] HNSW vector index created (VSS extension available)")
    except Exception:
        print("[ingest] VSS/HNSW index not available -- falling back to brute-force "
              "cosine search at query time (fine for a corpus this size)")

    con.execute("CREATE INDEX idx_chunks_article ON chunks (source, article)")
    n_rows = con.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    con.close()

    if persist:
        print(f"[ingest] {n_rows} chunks persisted to {DB_PATH}")


if __name__ == "__main__":
    build_vectorstore()
