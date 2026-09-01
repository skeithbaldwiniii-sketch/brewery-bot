from intelligence.task_queries import answer_task_question

questions = [
    "When is Max's Taphouse?",
    "When is Max's Taphouse event?",
    "When is the Max's Taphouse event?",
    '"When is Max\'s Taphouse event?"',
    "What day is Max's Taphouse event?",
]

for question in questions:
    print()
    print("=" * 60)
    print(f"QUESTION: {question}")
    print("=" * 60)
    print(answer_task_question(question))