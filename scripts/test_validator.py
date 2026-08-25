from app.intelligence.schema import FinancialQuery
from app.intelligence.validator import validate_query


def main():

    # --------------------------------------------------
    # TEST 1: Revenue growth normalization
    # --------------------------------------------------

    query1 = FinancialQuery(
        intent="metric_lookup",
        companies=["TCS"],
        metrics=["revenue growth"],
        periods=["FY25"],
        comparison=False,
        raw_query="What was TCS revenue growth in FY25?"
    )

    result1 = validate_query(query1)

    print("\nTEST 1: Revenue growth normalization")
    print(result1)


    # --------------------------------------------------
    # TEST 2: FCF normalization
    # --------------------------------------------------

    query2 = FinancialQuery(
        intent="metric_lookup",
        companies=["TCS"],
        metrics=["FCF"],
        periods=["FY25"],
        comparison=False,
        raw_query="What was TCS FCF in FY25?"
    )

    result2 = validate_query(query2)

    print("\nTEST 2: FCF normalization")
    print(result2)


    # TEST 3: Company comparison


    query3 = FinancialQuery(
        intent="comparison",
        companies=["TCS", "Infosys"],
        metrics=["revenue growth"],
        periods=["FY25"],
        comparison=True,
        raw_query="Compare TCS and Infosys revenue growth in FY25."
    )

    result3 = validate_query(query3)

    print("\nTEST 3: Company comparison")
    print(result3)


    # TEST 4: Time-period comparison / trend
   

    query4 = FinancialQuery(
        intent="trend_analysis",
        companies=["TCS"],
        metrics=["operating margin"],
        periods=["FY24", "FY25"],
        comparison=True,
        raw_query="How did TCS operating margin change from FY24 to FY25?"
    )

    result4 = validate_query(query4)

    print("\nTEST 4: Time-period comparison")
    print(result4)


    # TEST 5: Invalid company comparison

    query5 = FinancialQuery(
        intent="comparison",
        companies=["TCS"],
        metrics=["revenue"],
        periods=["FY25"],
        comparison=True,
        raw_query="Compare TCS revenue."
    )

    print("\nTEST 5: Invalid company comparison")

    try:
        result5 = validate_query(query5)
        print(result5)

    except ValueError as e:
        print("Validation Error:", e)


if __name__ == "__main__":
    main()