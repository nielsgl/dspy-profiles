import dspy

from dspy_profiles import profile


def main():
    """
    Minimal example showing how to configure and use a Retrieval Model (RM)
    via dspy-profiles. Ensure your profiles.toml contains something like:

    [search.rm]
    class_name = "ColBERTv2"
    url = "http://localhost:8893/api/search"
    """

    with profile("search"):
        rm = dspy.settings.rm
        print("Active RM:", type(rm).__name__)
        # If your RM exposes kwargs (many DSPy classes do), you can inspect them:
        print("RM kwargs:", getattr(rm, "kwargs", {}))

        # Your standard DSPy code can run here; any retrieval-aware modules
        # will use the configured RM automatically via dspy.context.


if __name__ == "__main__":
    main()
