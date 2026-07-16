# Agentic RAG Juridique — Droit Marocain

Système RAG agentique construit avec **LangGraph** (sans `create_agent`), répondant à des
questions de droit marocain (Code de la Famille / Moudawana, Code du Travail) à partir
d'une base documentaire vectorisée.

Projet réalisé dans le cadre de l'évaluation de fin de module *Agentic RAG* — Master IIBDCC,
Prof. RETAL Sara.

## Architecture

```
Question utilisateur
        │
        ▼
   ┌─────────┐   tool_calls    ┌───────┐
   │ planner │ ───────────────► │ tools │  retrieve_legal_context /
   │ (Grok)  │ ◄─────────────── │       │  get_article_by_number /
   └────┬────┘   after_tools    └───────┘  calculate_legal_deadline
        │ no tool_calls
        ▼
   ┌────────────┐   insuffisant
   │ reflection │ ───────────────► (retour au planner, borné à 3 tours)
   └─────┬──────┘
         │ suffisant
         ▼
       Réponse finale (avec citations d'articles)
```

Voir `notebooks/graph.mmd` pour le diagramme Mermaid complet (généré automatiquement
par `app.get_graph().draw_mermaid()`).

## Choix techniques

| Composant | Choix | Justification |
|---|---|---|
| Orchestration agentique | LangGraph (StateGraph manuel) | Imposé par le sujet — pas de `create_agent` |
| LLM | Grok (xAI), via l'API OpenAI-compatible `api.x.ai/v1` | Choix de l'étudiant |
| Embeddings | `intfloat/multilingual-e5-base` (local, sentence-transformers) | xAI n'expose pas d'API d'embeddings publique (vérifié juillet 2026) ; un modèle local multilingue gratuit couvre bien le français juridique |
| Vector store | **DuckDB** (fichier unique, local, `data/processed/legal.duckdb`) | Zéro infrastructure, pas de serveur à lancer ; la recherche par similarité utilise la fonction native `array_cosine_distance` (aucune extension à télécharger) ; les colonnes `law`/`article` étant de vraies colonnes SQL, `get_article_by_number` fait un lookup exact indexé plutôt qu'une recherche vectorielle approximative — un vrai atout d'un moteur relationnel pour du texte juridique structuré |
| Chunking | *Article-aware* : découpe d'abord sur les frontières "Article N", puis `RecursiveCharacterTextSplitter` en filet de sécurité | Un chunk qui coupe un article en deux nuit gravement à la pertinence en droit |
| Mémoire | `MemorySaver` (checkpointer LangGraph) par `thread_id` | Permet les questions de suivi dans une même conversation |

## Structure du projet

```
agentic-rag-legal/
├── data/
│   ├── raw/                  # textes juridiques sources (.txt)
│   └── processed/legal.duckdb  # base DuckDB persistée (générée par `ingest`)
├── src/
│   ├── ingest.py             # chargement, chunking article-aware, vectorisation
│   ├── llm.py                # wrapper Grok (xAI)
│   ├── tools.py              # 4 outils de l'agent (requêtes SQL/vectorielles sur DuckDB)
│   └── graph.py              # graphe LangGraph (state, nodes, edges, mémoire)
├── evaluation/
│   └── eval_questions.py     # 10 questions simples + 10 complexes, mesure temps/pertinence
├── notebooks/
│   └── graph.mmd             # visualisation du graphe
├── main.py                   # CLI (ingest / ask / chat)
├── requirements.txt
└── .env.example
```

## Installation

```bash
# 1. Se placer dans le dossier du projet
cd agentic-rag-legal

# 2. Créer un environnement virtuel
python3 -m venv venv

# 3. Activer l'environnement virtuel
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows (cmd)
venv\Scripts\Activate.ps1       # Windows (PowerShell)

# 4. Installer les dépendances dans l'environnement virtuel
pip install --upgrade pip
pip install -r requirements.txt

# 5. Configurer les variables d'environnement
cp .env.example .env
# éditer .env : ajouter XAI_API_KEY (https://console.x.ai)
```

⚠️ Pense à réactiver l'environnement virtuel (`source venv/bin/activate`) à chaque
nouvelle session de terminal avant de lancer `python main.py ...`. Pour en sortir :
`deactivate`.

## Utilisation

```bash
# 1. Construire la base vectorielle à partir de data/raw/
python main.py ingest

# 2. Poser une question
python main.py ask "Quelle est la durée du congé de maternité au Maroc ?"

# 3. Mode conversationnel (avec mémoire)
python main.py chat

# 4. Lancer l'évaluation complète (20 questions)
python evaluation/eval_questions.py
```

## Base documentaire

Extraits authentiques (traduction officielle) de :
- **Code de la Famille (Moudawana)** — Dahir n° 1-04-22 du 3 février 2004
- **Code du Travail** — Loi n° 65-99, Dahir n° 1-03-194 du 11 septembre 2003

⚠️ Pour un usage réel, il est recommandé de compléter `data/raw/` avec le texte
intégral des codes (actuellement des extraits représentatifs sont indexés — voir
la note en fin de chaque fichier `.txt`) et d'ajouter d'autres textes pertinents
(Code Pénal, Code des Obligations et Contrats, Constitution).

## Outils de l'agent

1. `retrieve_legal_context(query, k)` — recherche sémantique dans le corpus vectorisé
2. `get_article_by_number(law, article_number)` — lookup exact quand un numéro d'article est cité
3. `calculate_legal_deadline(start_date, days, weeks, months)` — calcul déterministe de délais légaux
4. `list_available_codes()` — introspection de la base pour gérer les questions hors périmètre

## Limites connues (voir rapport)

- Corpus actuellement composé d'extraits (≈35 articles par code) plutôt que du texte intégral (400+ / 589 articles)
- L'embedding multilingue général n'est pas fine-tuné sur le vocabulaire juridique marocain
- Le nœud de réflexion est un simple classifieur binaire LLM, pas une métrique RAGAS/faithfulness formelle
- Pas de gestion des textes en arabe (corpus français uniquement)
