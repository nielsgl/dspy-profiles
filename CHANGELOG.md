## 0.1.6 (2025-08-31)

### Feat

- 🚀 trigger final release process
- **release**: ✨ automate release process with commitizen
- **ci**: 🚀 refactor GitHub Actions workflows

### Fix

- **cicd**: grant write permissions to release job
- :green_heart: update release
- **ci**: 🐛 refactor release process for robustness
- **ci**: 🐛 correct release workflow logic
- **ci**: 🔧 migrate pre-commit config
- **ci**: 🐛 add checkout step before using local action
- **ci**: 🐛 switch to composite action

## 0.1.5 (2025-08-30)

### Feat

- :sparkles: implemented dspy-run cli interface

### Fix

- :bug: fixes cli documentation

### Refactor

- :fire: remove old main file
- :art: add more examples

## 0.1.4 (2025-08-28)

## v0.1.3 (2025-08-28)

## v0.1.2 (2025-08-28)

### Feat

- :sparkles: add version and test coverage

### Fix

- :white_check_mark: fix broken test

## v0.1.1 (2025-08-28)

## v0.1.0-alpha.1 (2025-08-28)

### Feat

- ✨ implement intelligent @with_profile decorator
- ✨ add support for dotted key TOML syntax
- **cli**: ✨ improve show command with readable output and json flag
- **api**: ✨ implement core profile management api
- **cli**: ✨ enhance init and list commands
- :sparkles: restructure the profile toml configuration to make it more intuitive
- **docs**: ✨ overhaul README and add advanced usage guide
- **docs**: ✨ overhaul README and add advanced usage guide
- **core**: ✨ add profile-aware caching
- **core**: ✨ add lm() shortcut utility
- **core**: ✨ add current_profile() introspection utility
- **cli**: ✨ add dspy profiles test command
- **cli**: ✨ add dspy profiles validate command
- **profiles**: ✨ implement profile composition with 'extends' and overrides
- **cli**: ✨ add run command to execute subprocesses with profiles
- **cli**: ✨ add diff command to compare profiles
- **cli**: ✨ add import command to create profiles from .env files
- **packaging**: 📦 configure project for PyPI and add docs dependencies
- :sparkles: implement remaining placeholders
- ✨ add run command to cli
- ✨ add pydantic validation for profiles
- ✨ apply all profile settings in context manager
- ✨ add python api with context manager and decorator
- ✨ make init command interactive
- ✨ implement ProfileLoader for configuration resolution
- ✨ implement core profile management CLI commands
- :sparkles: hello dspy!

### Fix

- :memo: fix typo
- 🐛 relax validation to support profile inheritance
- 🐛 relax validation to support profile inheritance
- **cli**: 🐛 fix HttpUrl serialization and improve show output
- **cli**: 🐛 resolve delete default and diff serialization errors
- **api**: 🐛 fix data corruption bugs in set and delete commands
- **core**: 🐛 revert to dspy.context to fix test regressions

### Refactor

- **cli**: ♻️ connect cli commands to the new core api
- **cli**: ♻️ modularize cli commands into separate files
- :recycle: ensure that profiles created during running of tests are separate from main profiles
- **core**: 🎨 improve docstrings and type hinting for docs
- **core**: ♻️ implement robust precedence logic and fix LM instantiation
- ♻️ make ProfileLoader stateless
- ✨ adopt robust, testable architecture for config and cli
