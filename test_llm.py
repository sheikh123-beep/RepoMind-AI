from services.llm_service import generate_answer


prompt = """
Define a Python function in simple words.
Answer in maximum 3 lines.
"""

answer = generate_answer(prompt)

print("\nAI ANSWER:")
print(answer)