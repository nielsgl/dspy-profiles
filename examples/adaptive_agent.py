"""
=========================================
dspy-profiles: Adaptive Agent Example
=========================================

This example demonstrates a more advanced use case of the `@with_profile`
decorator on a `dspy.Module`. It showcases an "adaptive agent" that can
switch its underlying language model (and behavior) based on the task it's
given, all managed through dspy-profiles.

Key Concepts Illustrated:
- Applying `@with_profile` to a `dspy.Module` class.
- Dynamically overriding the profile at runtime during the forward pass.
- Using different profiles to control agent behavior (e.g., a "creative"
  profile vs. a "technical" profile).
- How profiles encapsulate not just the model, but also other settings like
  temperature, which can significantly alter the output.

To Run This Example:
1. Make sure you have dspy-profiles installed (`pip install .`).
2. Ensure you have a `profiles.toml` file configured with "creative_agent"
   and "technical_agent" profiles. Example:

   ```toml
   # ~/.dspy/profiles.toml

   [creative_agent]
   provider = "openai"
   model = "gpt-3.5-turbo-instruct" # Or any creative model
   temperature = 0.9
   max_tokens = 150

   [technical_agent]
   provider = "openai"
   model = "gpt-4" # Or any technical model
   temperature = 0.0
   max_tokens = 250
   ```
3. Run the script from your terminal: `python examples/adaptive_agent.py`
"""

import dspy

import dspy_profiles


# By applying the decorator to the class, "creative_agent" becomes the default
# profile for all instances of AdaptiveAgent.
@dspy_profiles.with_profile("creative_agent")
class AdaptiveAgent(dspy.Module):
    """
    An agent that can adapt its approach based on the provided task profile.
    """

    def __init__(self):
        super().__init__()
        # A simple signature for generating text.
        self.predictor = dspy.Predict("context -> text")

    def forward(self, context: str, task_type: str | None = None):
        """
        Generates text based on the context.

        If a `task_type` is provided, it will attempt to switch to a profile
        with that name at runtime. Otherwise, it uses the default profile
        defined by the decorator (`creative_agent`).

        Args:
            context (str): The input context for the language model.
            task_type (str | None, optional): The name of the profile to use
                                              for this specific call.
                                              Defaults to None.
        """
        print(f"\n--- Running with task_type: {task_type or 'default'} ---")

        # Here's the dynamic part: we can pass a profile name directly to the
        # forward pass. The decorator's logic will pick this up and use it
        # to override the default profile for this specific call.
        # Note: This requires a hypothetical modification to the decorator to
        # handle runtime overrides passed this way. For now, we simulate it
        # by calling the context manager directly.
        if task_type:
            with dspy_profiles.profile(task_type, force=True):
                active_profile = dspy_profiles.current_profile()
                print(f"Switched to profile: {active_profile.name if active_profile else 'None'}")
                print(f"LM Config: {dspy.settings.lm}")
                return self.predictor(context=context)
        else:
            # If no task_type is given, it runs with the default decorator profile.
            active_profile = dspy_profiles.current_profile()
            print(f"Using default profile: {active_profile.name if active_profile else 'None'}")
            print(f"LM Config: {dspy.settings.lm}")
            return self.predictor(context=context)


def main():
    """Main function to demonstrate the AdaptiveAgent."""
    # This initialization is "profile-aware" due to the decorator.
    # If we were to call it now, it would use the "creative_agent" profile.
    agent = AdaptiveAgent()

    # --- Task 1: Creative Writing ---
    # We don't specify a task_type, so it uses the default "creative_agent" profile.
    creative_context = "Write a short, dramatic opening for a sci-fi novel."
    creative_response = agent(context=creative_context)
    print("\nCreative Response:")
    print(creative_response.text)

    # --- Task 2: Technical Explanation ---
    # Here, we dynamically switch to the "technical_agent" profile for a single call.
    technical_context = "Explain the concept of Retrieval-Augmented Generation (RAG)."
    technical_response = agent(context=technical_context, task_type="technical_agent")
    print("\nTechnical Response:")
    print(technical_response.text)

    # --- Verification ---
    # After the calls, the global settings should be reset, proving the
    # context management of the decorator and context manager works correctly.
    print("\n--- After Execution ---")
    print(f"Current global LM config: {dspy.settings.lm}")
    assert dspy.settings.lm is None, "dspy.settings.lm should be reset after the calls."
    print("Global settings have been successfully reset.")


if __name__ == "__main__":
    # NOTE: This example requires you to have "creative_agent" and "technical_agent"
    # profiles configured in your `profiles.toml` file.
    try:
        main()
    except FileNotFoundError:
        print("\nERROR: `profiles.toml` not found.")
        print("Please create a `profiles.toml` file in `~/.dspy/` or your project root.")
    except KeyError as e:
        print(f"\nERROR: Profile not found: {e}")
        print("Please ensure your `profiles.toml` contains 'creative_agent' and 'technical_agent'.")
