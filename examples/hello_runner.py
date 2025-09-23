"""Demonstrate running a script under a profile via `dspy-run`.

Invoke this file with `uv run dspy-run --profile default -- python examples/hello_runner.py`
or via the project helper script. The wrapper sets `DSPY_PROFILE` for us,
so no context manager is required inside the script itself.
"""

import os

import dspy

print(f"{os.getenv('DSPY_PROFILE')=}")
for key in os.environ:
    if key.startswith("DSPY"):
        print(f"{key}, {os.getenv(key)}")

# No need for a context manager—the active profile is applied by dspy-run.
predictor = dspy.Predict("question -> answer")
result = predictor(question="What is the capital of Mexico?")
print(f"The answer is: {result.answer}.")
