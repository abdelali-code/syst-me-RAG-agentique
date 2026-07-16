"""
Tools available to the Agentic RAG graph.

Per the assignment brief, the agent must have real "tool use" capability,
not just a single retrieval step baked into the graph. We expose:

  1. retrieve_legal_context  -> semantic search over the DuckDB-stored chunks
     (cosine similarity via DuckDB's native array_cosine_distance)
  2. get_article_by_number   -> exact SQL lookup when the user cites a specific
     article ("article 53 du code du travail"), which a pure similarity
     search sometimes misses because "article 53" is a poor semantic query.
     This is a direct benefit of storing article numbers as a real SQL
     column instead of opaque vector-store metadata.
  3. calculate_legal_deadline -> a small deterministic calculator for the
     many day/month deadlines that appear throughout Moroccan legal codes
  4. list_available_codes    -> lets the agent introspect what's actually
     in the knowledge base, useful when a question is out of scope
"""
from datetime import datetime, timedelta
from langchain_core.tools import tool

from src.ingest import get_connection, get_embedder, EMBEDDING_DIM

_embedder = None


def _get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = get_embedder()
    return _embedder


@tool
def retrieve_legal_context(query: str, k: int = 5) -> str:
    """Search the Moroccan legal corpus (Code de la Famille / Moudawana,
    Code du Travail) for passages relevant to the query. Use this for any
    question about rights, obligations, procedures, deadlines, or definitions
    found in Moroccan family law or labor law. Returns the top-k matching
    article excerpts with their source and article number.
    """
    query_vector = _get_embedder().embed_query(query)

    con = get_connection(read_only=True)
    rows = con.execute(
        f"""
        SELECT source, article, content,
               array_cosine_distance(embedding, ?::FLOAT[{EMBEDDING_DIM}]) AS distance
        FROM chunks
        ORDER BY distance ASC
        LIMIT ?
        """,
        [query_vector, k],
    ).fetchall()
    con.close()

    if not rows:
        return "Aucun passage pertinent trouvé dans la base documentaire."

    formatted = []
    for source, article, content, distance in rows:
        similarity = 1 - distance
        formatted.append(
            f"[Source: {source} | Article {article} | pertinence={similarity:.2f}]\n{content}"
        )
    return "\n\n---\n\n".join(formatted)


@tool
def get_article_by_number(law: str, article_number: str) -> str:
    """Look up a specific article by its exact number, when the user cites
    one directly (e.g. 'article 53 du code du travail', 'article 400 de la
    moudawana'). `law` should be either 'travail' or 'famille'. This is more
    reliable than semantic search for exact citations, since 'article 53' is
    not semantically distinctive on its own -- it's a plain indexed SQL
    lookup rather than a vector search.
    """
    source_hint = "code_travail" if "trav" in law.lower() else "code_famille"

    con = get_connection(read_only=True)
    row = con.execute(
        "SELECT source, article, content FROM chunks "
        "WHERE source LIKE ? AND article = ? LIMIT 1",
        [f"%{source_hint}%", article_number.strip()],
    ).fetchone()
    con.close()

    if row:
        source, article, content = row
        return f"[Source: {source} | Article {article}]\n{content}"

    return (
        f"Article {article_number} non trouvé dans la base pour '{law}'. "
        f"Il est possible qu'il ne fasse pas partie du sous-ensemble indexé, "
        f"ou que le numéro soit incorrect."
    )


@tool
def calculate_legal_deadline(start_date: str, days: int = 0, weeks: int = 0, months: int = 0) -> str:
    """Compute a deadline date given a start date (format YYYY-MM-DD) and a
    duration in days/weeks/months, as commonly required by Moroccan legal
    procedures (e.g. 90-day appeal window under article 65 of the Code du
    Travail, 14-week maternity leave under article 152 of the Moudawana).
    """
    try:
        start = datetime.strptime(start_date.strip(), "%Y-%m-%d")
    except ValueError:
        return "Format de date invalide. Utilisez YYYY-MM-DD."

    total_days = days + weeks * 7 + months * 30  # approximation for months
    deadline = start + timedelta(days=total_days)
    return (
        f"Date de départ : {start.date()}\n"
        f"Durée : {days}j + {weeks}sem + {months}mois (~{total_days} jours)\n"
        f"Date limite calculée : {deadline.date()}"
    )


@tool
def list_available_codes() -> str:
    """List which legal codes/texts are currently indexed in the knowledge
    base, so the agent can tell the user what is and isn't in scope."""
    con = get_connection(read_only=True)
    rows = con.execute("SELECT DISTINCT source FROM chunks ORDER BY source").fetchall()
    con.close()
    sources = [r[0] for r in rows]
    return "Textes juridiques disponibles dans la base :\n" + "\n".join(f"- {s}" for s in sources)


ALL_TOOLS = [retrieve_legal_context, get_article_by_number, calculate_legal_deadline, list_available_codes]
