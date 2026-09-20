conversation_history = []


def get_history() -> str:
    return "\n".join(conversation_history)


def add_exchange(question: str, answer: str):
    conversation_history.append(f"User: {question}")
    conversation_history.append(f"Assistant: {answer}")

    if len(conversation_history) > 10:
        conversation_history.pop(0)
        conversation_history.pop(0)