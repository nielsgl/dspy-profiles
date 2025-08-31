from dspy_profiles import __version__


def define_env(env) -> None:
    env.variables.version = __version__
