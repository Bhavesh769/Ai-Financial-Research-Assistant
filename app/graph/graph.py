from langgraph.graph import StateGraph, START, END

from app.graph.state import GraphState
from app.graph.nodes import analyze_query_node
from app.graph.retrieval_nodes import (
    metric_lookup_node,
    comparison_node,
    trend_analysis_node,
    unknown_node,
)
from app.graph.router import route_query
from app.graph.answer_node import answer_node


def build_graph():

    graph = StateGraph(GraphState)

    # Nodes
    graph.add_node(
        "analyze_query",
        analyze_query_node,
    )

    graph.add_node(
        "metric_lookup",
        metric_lookup_node,
    )

    graph.add_node(
        "comparison",
        comparison_node,
    )

    graph.add_node(
        "trend_analysis",
        trend_analysis_node,
    )

    graph.add_node(
        "unknown",
        unknown_node,
    )

    graph.add_node(
        "answer",
        answer_node,
    )

    # START → Analysis
    graph.add_edge(
        START,
        "analyze_query",
    )

    # Analysis → Router → Retrieval
    graph.add_conditional_edges(
        "analyze_query",
        route_query,
        {
            "metric_lookup": "metric_lookup",
            "comparison": "comparison",
            "trend_analysis": "trend_analysis",
            "unknown": "unknown",
        },
    )

    # Retrieval → Answer
    graph.add_edge(
        "metric_lookup",
        "answer",
    )

    graph.add_edge(
        "comparison",
        "answer",
    )

    graph.add_edge(
        "trend_analysis",
        "answer",
    )

    graph.add_edge(
        "unknown",
        "answer",
    )

    # Answer → END
    graph.add_edge(
        "answer",
        END,
    )

    return graph.compile()