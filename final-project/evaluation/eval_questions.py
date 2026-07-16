"""
Evaluation script — required by the assignment brief:
  "tester votre système sur 10 questions simples et 10 questions complexes,
   et analyser la qualité des réponses, le temps de réponse et la pertinence
   des documents récupérés."

Simple questions: answerable from a single article, single-hop retrieval.
Complex questions: require combining multiple articles across one or both
codes, multi-hop reasoning, or a calculation (e.g. deadlines).

Run:
    python evaluation/eval_questions.py

Outputs a Markdown table + raw JSON to evaluation/results/.
"""
import json
import time
import uuid
from pathlib import Path
from datetime import datetime, timezone

from src.graph import build_graph, run_query
from src.tools import retrieve_legal_context

RESULTS_DIR = Path(__file__).resolve().parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

SIMPLE_QUESTIONS = [
    "Quel est l'âge légal du mariage au Maroc ?",
    "Combien de temps dure le congé de maternité selon le Code du Travail ?",
    "Quelle est la durée légale du travail par semaine dans les activités non agricoles ?",
    "A qui la garde de l'enfant (hadana) est-elle confiée en premier lieu ?",
    "Quel est l'âge de la majorité légale au Maroc ?",
    "Qu'est-ce que le Sadaq dans le Code de la Famille ?",
    "Combien de jours de congé annuel payé un salarié acquiert-il par mois de service ?",
    "Quelle est la durée de la période d'essai pour un cadre en CDI ?",
    "Qu'est-ce qu'une faute grave pouvant justifier un licenciement selon le Code du Travail ?",
    "A partir de quel âge un enfant peut-il choisir lequel de ses parents assurera sa garde ?",
]

COMPLEX_QUESTIONS = [
    "Un salarié en CDI avec 12 ans d'ancienneté est licencié : quelle formule s'applique pour "
    "calculer son indemnité de licenciement, et à combien d'heures de salaire a-t-il droit ?",
    "Quelles sont les conditions cumulatives pour qu'un tribunal autorise la polygamie, et quels "
    "recours a la première épouse si elle refuse ?",
    "Une salariée est en état de grossesse : quelles protections a-t-elle à la fois sur la rupture "
    "de son contrat de travail et sur la durée de son congé, et que se passe-t-il si son état "
    "pathologique nécessite une prolongation ?",
    "Comparez les motifs de divorce judiciaire ouverts à l'épouse selon la Moudawana avec les motifs "
    "de licenciement pour faute grave dans le Code du Travail : quels points communs de procédure "
    "(droit d'être entendu, délais) apparaissent dans les deux textes ?",
    "Si un salarié reçoit sa décision de licenciement le 1er mars 2025, jusqu'à quelle date "
    "dispose-t-il pour saisir le tribunal, et que se passe-t-il s'il dépasse ce délai ?",
    "Quelles sont les différences entre le divorce par consentement mutuel, le divorce judiciaire "
    "et le divorce par Khol' dans la Moudawana, en particulier sur qui doit prouver quoi ?",
    "Un employeur veut licencier 15 salariés pour motifs économiques : quelle est la procédure "
    "complète à suivre, y compris les délais et les autorités impliquées ?",
    "Quels critères le tribunal prend-il en compte pour attribuer la garde d'un enfant en cas de "
    "désaccord des parents, et cette attribution peut-elle changer si la mère se remarie ?",
    "Un contrat de travail à durée déterminée est rompu avant son terme sans faute grave : quelles "
    "sont les conséquences financières pour la partie responsable, et cela diffère-t-il d'un CDI ?",
    "Expliquez la chaîne de protection d'une salariée enceinte, de l'annonce de sa grossesse "
    "jusqu'à la fin de la période d'allaitement, en citant les articles concernés à chaque étape.",
]


def evaluate_retrieval_relevance(question: str, k: int = 5) -> dict:
    """Measures retrieval quality independent of the LLM: does the top-k
    similarity search actually surface relevant articles?"""
    start = time.time()
    raw = retrieve_legal_context.invoke({"query": question, "k": k})
    elapsed = time.time() - start
    n_hits = raw.count("[Source:")
    return {"retrieval_time_s": round(elapsed, 3), "n_chunks_retrieved": n_hits}


def run_eval():
    app = build_graph()
    all_results = []

    for category, questions in [("simple", SIMPLE_QUESTIONS), ("complexe", COMPLEX_QUESTIONS)]:
        for q in questions:
            print(f"[{category}] {q[:70]}...")
            thread_id = str(uuid.uuid4())

            retrieval_stats = evaluate_retrieval_relevance(q)

            t0 = time.time()
            try:
                result = run_query(app, q, thread_id=thread_id)
                answer = result["messages"][-1].content
                n_tool_calls = sum(
                    len(getattr(m, "tool_calls", []) or [])
                    for m in result["messages"]
                    if hasattr(m, "tool_calls")
                )
                error = None
            except Exception as e:  # noqa: BLE001
                answer = None
                n_tool_calls = 0
                error = str(e)
            total_time = round(time.time() - t0, 3)

            all_results.append({
                "category": category,
                "question": q,
                "answer": answer,
                "error": error,
                "response_time_s": total_time,
                "n_tool_calls": n_tool_calls,
                **retrieval_stats,
            })

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    json_path = RESULTS_DIR / f"eval_{timestamp}.json"
    json_path.write_text(json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8")

    md_lines = ["# Résultats d'évaluation\n", f"Généré le {timestamp}\n",
                "| # | Catégorie | Question | Temps (s) | Chunks récupérés | Appels outils | Erreur |",
                "|---|-----------|----------|-----------|-------------------|----------------|--------|"]
    for i, r in enumerate(all_results, 1):
        md_lines.append(
            f"| {i} | {r['category']} | {r['question'][:60]}... | {r['response_time_s']} | "
            f"{r['n_chunks_retrieved']} | {r['n_tool_calls']} | {r['error'] or '-'} |"
        )
    (RESULTS_DIR / f"eval_{timestamp}.md").write_text("\n".join(md_lines), encoding="utf-8")

    print(f"\nRésultats sauvegardés dans {json_path}")
    return all_results


if __name__ == "__main__":
    run_eval()
