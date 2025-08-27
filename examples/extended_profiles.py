import dspy

from dspy_profiles import current_profile, profile


def main():
    """
    This example demonstrates profile inheritance using the `extends` keyword.

    To run this, you'll need a `profiles.toml` with a structure like this:

    [base_model]
    lm.model = "azure/gpt-4o-mini"
    lm.api_key = "your_api_key"
    lm.api_base = "your_api_base"

    [creative_child]
    extends = "base_model"
    lm.temperature = 0.9
    """
    print("Running extended profiles example...")

    question = "Tell me a fun fact about the ocean."
    print(f"Question: {question}")

    # --- Using the "creative_child" profile ---
    # This profile inherits settings from "base_model" and adds its own.
    print("\n--- Using 'creative_child' profile ---")
    with profile("creative_child"):
        active_profile = current_profile()
        if active_profile:
            print(f"Active profile: {active_profile.name}")
            print(f"Final LM config: {active_profile.lm}")

        predictor = dspy.Predict("question -> fun_fact")
        result = predictor(question=question)
        print(f"Fun Fact: {result.fun_fact}")


if __name__ == "__main__":
    main()
