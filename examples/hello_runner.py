import os

import dspy

print(f"{os.getenv('DSPY_PROFILE')=}")
for key in os.environ:
    if key.startswith("DSPY"):
        print(f"{key}, {os.getenv(key)}")
# No need for a context manager, the profile is active!
predictor = dspy.Predict("question -> answer")
result = predictor(question="What is the capital of Mexico?")
print(f"The answer is: {result.answer}.")
