from app.graph.state import GraphState
from app.graph.retrieval_nodes import metric_lookup_node
from app.intelligence.schema import FinancialQuery


def main():

    state = GraphState()

    state.user_query = "What was TCS revenue growth in FY25?"

    state.financial_query = FinancialQuery(
        intent="metric_lookup",
        companies=["TCS"],
        metrics=["revenue_growth"],
        periods=["FY25"],
        comparison=False,
        raw_query=state.user_query,
    )

    state = metric_lookup_node(state)

    print("\nRETRIEVED CONTEXT\n")
    print(state.context)


if __name__ == "__main__":
    main()