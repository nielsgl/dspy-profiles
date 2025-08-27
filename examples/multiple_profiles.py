import dspy

from dspy_profiles import current_profile, profile


def main():
    """
    This example demonstrates how to use multiple profiles in the same script
    and how to inspect the currently active profile. It assumes you have a "default"
    profile and a "creative" profile defined in your `profiles.toml`.
    """
    print("Running multiple profiles example...")

    question = "Write a short poem about the moon."
    print(f"Question: {question}")

    # --- Using the "default" profile ---
    print("\n--- Using 'default' profile ---")
    with profile("default"):
        # The `current_profile()` function returns the active profile object.
        active_profile = current_profile()
        if active_profile:
            print(f"Active profile: {active_profile.name}")

        predictor_default = dspy.Predict("question -> poem")
        result_default = predictor_default(question=question)
        print(f"Poem (default): {result_default.poem}")

    # --- Using the "creative" profile ---
    print("\n--- Using 'creative' profile ---")
    with profile("creative"):
        active_profile = current_profile()
        if active_profile:
            print(f"Active profile: {active_profile.name}")

        predictor_creative = dspy.Predict("question -> poem")
        result_creative = predictor_creative(question=question)
        print(f"Poem (creative): {result_creative.poem}")


if __name__ == "__main__":
    main()
