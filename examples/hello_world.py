import dspy

from dspy_profiles import profile


def main():
    """
    This example demonstrates the basic usage of the dspy-profiles library.
    It activates the "default" profile from your `profiles.toml` and uses it
    to configure dspy for a simple prediction task.
    """
    print("Running basic hello world example...")

    # The `profile` context manager activates the specified profile.
    # In this case, it loads the configuration for the "default" profile.
    # All dspy calls within this block will use the settings from that profile,
    # such as the language model, API keys, and other configurations.
    with profile("default"):
        # dspy.Predict creates a simple predictor module. The signature "question -> answer"
        # tells DSPy that this module takes a "question" as input and is expected
        # to produce an "answer" as output.
        predictor = dspy.Predict("question -> answer")

        # When the predictor is called, it uses the configured language model
        # to generate a response based on the provided question.
        result = predictor(question="What is the color of the sky?")

        # The result object contains the full completion from the language model,
        # including the predicted answer.
        print("Question: What is the color of the sky?")
        print(f"Answer: {result.answer}")


if __name__ == "__main__":
    main()
