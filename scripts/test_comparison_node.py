from app.graph.state import GraphState
from app.graph.retrieval_nodes import comparison_node
from app.intelligence.schema import FinancialQuery


def main():

    state = GraphState()

    state.user_query = (
        "Compare TCS and Infosys revenue growth in FY25."
    )

    state.financial_query = FinancialQuery(
        intent="comparison",
        companies=["TCS", "Infosys"],
        metrics=["revenue_growth"],
        periods=["FY25"],
        comparison=True,
        raw_query=state.user_query,
    )

    state = comparison_node(state)

    print("\nCOMPARISON CONTEXT\n")
    print(state.context)


if __name__ == "__main__":
    main()