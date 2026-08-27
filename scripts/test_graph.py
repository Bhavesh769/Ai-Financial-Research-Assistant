from app.graph.graph import build_graph


def main():

    graph = build_graph()

    queries = [
        "What was TCS revenue growth in FY25?",
        "Compare TCS and Infosys revenue growth in FY25.",
        "How did TCS operating margin change from FY24 to FY25?",
    ]

    for query in queries:

        print("\n" + "=" * 70)
        print("QUERY:", query)
        print("=" * 70)

        initial_state = {
            "user_query": query,
            "financial_query": None,
            "context": "",
            "answer": "",
        }

        try:

            result = graph.invoke(initial_state)

            print("\nIntent:")
            print(result["financial_query"].intent)

            print("\nRetrieved Context:")
            print(result["context"][:2000])

        except Exception as e:

            print("\nERROR:")
            print(e)


if __name__ == "__main__":
    main()