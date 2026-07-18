"""
CLI entrypoint for the Agentic RAG Juridique system.

Usage:
    python main.py ingest                # build the vector store from data/raw/
    python main.py chat                  # interactive chat loop
    python main.py ask "votre question"  # single question, one-shot
    python main.py serve                 # start the HTTP API for the Flutter app
"""
import sys
import uuid

from src.graph import build_graph, run_query


def cmd_ingest():
    from src.ingest import build_vectorstore
    build_vectorstore()


def cmd_ask(question: str):
    app = build_graph()
    result = run_query(app, question, thread_id=str(uuid.uuid4()))
    print("\n=== RÉPONSE ===")
    print(result["messages"][-1].content)


def cmd_serve():
    import uvicorn
    uvicorn.run("src.api:app", host="127.0.0.1", port=8000, reload=True)


def cmd_chat():
    app = build_graph()
    thread_id = str(uuid.uuid4())
    print("Assistant Juridique Marocain (Agentic RAG) — tapez 'quit' pour sortir\n")
    while True:
        try:
            question = input("Vous > ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if question.lower() in {"quit", "exit", "q"}:
            break
        if not question:
            continue
        result = run_query(app, question, thread_id=thread_id)
        print(f"\nAssistant > {result['messages'][-1].content}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    if command == "ingest":
        cmd_ingest()
    elif command == "ask":
        cmd_ask(" ".join(sys.argv[2:]))
    elif command == "chat":
        cmd_chat()
    elif command == "serve":
        cmd_serve()
    else:
        print(__doc__)
        sys.exit(1)
