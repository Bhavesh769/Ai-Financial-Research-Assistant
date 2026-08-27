from app.graph.graph import build_graph


def main():

    graph = build_graph()

    print("=" * 70)
    print("AI FINANCIAL RESEARCH ASSISTANT")
    print("=" * 70)

    query = input("\nAsk your financial question: ")

    initial_state = {
        "user_query": query,
        "financial_query": None,
        "context": "",
        "answer": "",
    }

    try:

        result = graph.invoke(initial_state)

        print("\n" + "=" * 70)
        print("FINAL ANSWER")
        print("=" * 70)

        print(result["answer"])

    except Exception as e:

        print("\nERROR:")
        print(e)


if __name__ == "__main__":
    main()