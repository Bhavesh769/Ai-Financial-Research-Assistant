from app.intelligence.classifier import classify_query


def main():

    queries = [
        "What was TCS revenue growth in FY25?",
        "Compare TCS and Infosys revenue growth in FY25.",
        "How did TCS operating margin change from FY24 to FY25?",
        "What was TCS free cash flow in FY25?",
        "What drove TCS revenue growth in FY25?",
    ]

    for query in queries:

        print("\n" + "=" * 70)
        print("QUERY:", query)

        try:
            result = classify_query(query)

            print("\nStructured Query:")
            print(result)

        except Exception as e:
            print("\nERROR:")
            print(e)


if __name__ == "__main__":
    main()