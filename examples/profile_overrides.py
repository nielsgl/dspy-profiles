import dspy

from dspy_profiles import current_profile, profile


def main():
    """
    This example demonstrates how to override profile settings at runtime.
    This is useful for experimenting with different parameters without
    modifying your `profiles.toml` file.
    """
    print("Running profile overrides example...")

    question = "What is the capital of France?"
    print(f"Question: {question}")

    # --- Using the "default" profile with no overrides ---
    print("\n--- Using 'default' profile ---")
    with profile("default"):
        active_profile = current_profile()
        if active_profile:
            print(f"Active profile: {active_profile.name}")
            print(f"LM config: {active_profile.lm}")

        predictor_default = dspy.Predict("question -> answer")
        result_default = predictor_default(question=question)
        print(f"Answer (default): {result_default.answer}")

    # --- Overriding the temperature setting ---
    print("\n--- Overriding 'temperature' in 'default' profile ---")
    # You can pass keyword arguments to the profile context manager to override
    # any setting in the loaded profile. Here, we override the 'temperature'
    # in the language model settings.
    with profile("default", lm={"temperature": 0.9}):
        active_profile = current_profile()
        if active_profile:
            print(f"Active profile: {active_profile.name}")
            print(f"LM config (overridden): {active_profile.lm}")

        predictor_override = dspy.Predict("question -> answer")
        result_override = predictor_override(question=question)
        print(f"Answer (overridden): {result_override.answer}")


if __name__ == "__main__":
    main()
