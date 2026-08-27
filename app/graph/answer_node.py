from app.llm.ollama import generate_answer


def answer_node(state):
    """
    Generate the final answer using the user's question
    and retrieved financial context.
    """

    query = state["user_query"]
    context = state["context"]

    answer = generate_answer(
        query=query,
        context=context,
    )

    state["answer"] = answer

    return state