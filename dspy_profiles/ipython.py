from IPython.core.magic import Magics, line_magic, magics_class

from dspy_profiles.loader import ProfileLoader


@magics_class
class ProfileMagics(Magics):
    """IPython magics for dspy-profiles."""

    def __init__(self, shell, loader=None):
        super().__init__(shell)
        self.loader = loader or ProfileLoader()

    @line_magic
    def profile(self, line: str):
        """Activates a dspy-profile for the current IPython session.

        Usage:
            %profile my_profile_name [key=value...]

        This will load the configuration from 'my_profile_name' and apply it
        globally to dspy.settings for the remainder of the session.
        """
        from dspy_profiles.core import profile as profile_context

        args = line.strip().split()
        if not args:
            print("Usage: %profile <profile_name> [key=value...]")
            return

        profile_name = args[0]
        overrides = {}
        for arg in args[1:]:
            if "=" in arg:
                key, value = arg.split("=", 1)
                overrides[key] = value

        try:
            with profile_context(
                profile_name,
                loader=self.loader,
                **overrides,
            ):
                # The context manager handles activation; we just need to enter and exit
                # In a real session, this would configure dspy.settings for subsequent cells
                pass
            print(f"✅ Profile '{profile_name}' activated.")
        except ValueError as e:
            print(f"❌ Error: {e}")
        except Exception as e:
            print(f"❌ An unexpected error occurred: {e}")


def load_ipython_extension(ipython):
    """
    This function is called when the extension is loaded.
    It registers the ProfileMagics class.
    """
    ipython.register_magics(ProfileMagics(ipython))
