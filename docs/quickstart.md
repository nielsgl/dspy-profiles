# Quickstart

This guide will walk you through the basics of setting up and using `dspy-profiles`.

## 1. Installation

First, install the package from PyPI:

```bash
pip install dspy-profiles
```

## 2. Initialize a Profile

The easiest way to get started is with the interactive `init` command. This will create a `default` profile for you.

```bash
dspy-profiles init
```

This command will ask you a few questions and then create the configuration file at `~/.dspy/profiles.toml`.

## 3. View Your Profile

You can view the contents of any profile with the `show` command:

```bash
dspy-profiles show default
```

## 4. Use in Python with the Context Manager

Activate your profile in any Python script or notebook using the `profile` context manager.

```python
import dspy
from dspy_profiles import profile

# DSPy settings are configured automatically within this block
with profile("default"):
    # Your DSPy code here
    predictor = dspy.Predict("question -> answer")
    result = predictor(question="What is the color of the sky?")
    print(result.answer)
```

Any DSPy calls made inside the `with` block will use the settings from your `default` profile. Outside the block, the global DSPy settings are left untouched.

## 5. Use with the CLI `run` Command

For running entire scripts, the `run` command is the most convenient option. It activates a profile for the entire duration of the script's execution.

Create a file named `my_script.py`:

```python
# my_script.py
import dspy

# No need for the context manager, the profile is active!
predictor = dspy.Predict("question -> answer")
result = predictor(question="What is the capital of Spain?")
print(f"The capital of Spain is {result.answer}.")
```

Now, run it with your profile:

```bash
dspy-profiles run --profile default -- python my_script.py
