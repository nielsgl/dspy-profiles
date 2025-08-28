"""
=========================================
dspy-profiles: Basic Decorator Usage
=========================================

This example demonstrates the most basic usage of the `@with_profile`
decorator. The decorator is applied to a standard Python function that
contains DSPy logic.

Key Concepts Illustrated:
- Applying the `@with_profile` decorator to a function.
- How the decorator automatically loads a specified profile ("default" in this
  case) and configures `dspy.settings` before the function runs.
- The simplicity of injecting comprehensive LM configurations into your DSPy
  programs without boilerplate code.

To Run This Example:
1. Make sure you have dspy-profiles installed (`pip install .`).
2. Ensure you have a `profiles.toml` file with a "default" profile.
   Example:

   ```toml
   # ~/.dspy/profiles.toml

   [default]
   provider = "openai"
   model = "gpt-3.5-turbo-instruct"
   api_key = "YOUR_OPENAI_API_KEY" # Or set the OPENAI_API_KEY environment variable
   ```
3. Run the script from your terminal: `python examples/decorator_usage.py`
"""

import dspy

from dspy_profiles import with_profile


# The @with_profile decorator is applied here.
# When `my_dspy_program` is called, dspy-profiles will:
# 1. Look for a profile named "default" in your `profiles.toml`.
# 2. Load its configuration (e.g., model, provider, api_key).
# 3. Temporarily apply these settings to `dspy.settings`.
# 4. Execute the function.
# 5. Automatically clean up and restore the original `dspy.settings` afterward.
@with_profile("default")
def my_dspy_program(question):
    """
    A simple DSPy program that uses a Predict module to answer a question.
    The underlying language model is configured by the @with_profile decorator.
    """
    # This Predict module will automatically use the LM configured by the active profile.
    predictor = dspy.Predict("question -> answer")
    return predictor(question=question)


def main():
    """Main function to run the example."""
    # Calling this function triggers the decorator's logic.
    question = "What is the capital of Spain?"
    result = my_dspy_program(question)
    print(f"Question: {question}")
    print(f"Answer: {result.answer}")


if __name__ == "__main__":
    main()
