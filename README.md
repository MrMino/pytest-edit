# pytest-edit

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/:pytest-edit)

A simple Pytest plugin for opening editor on the failed tests.

## Installation & usage

Install with:

```
pip install pytest-edit
```

Usage:

```
pytest --edit
```

## Setting the right editor & editor support

Use `$EDITOR` environment variable to set the editor that should be opened.
E.g. you can add `export EDITOR=vim` line to your `.bashrc` or `.zshrc` to set
the editor to `vim`.

If no editor is set, the defaults are `vi` for POSIX platforms and `notepad`
for Windows.

The plugin tries to be cleaver about the options given to the detected editor.
If something is not working properly for you, don't hesitate to
[open an issue](https://github.com/MrMino/pytest-edit/issues).

**I have not tested 90% of the editor support** - there are at least 3
platforms with tens of different editors. I use Linux and NeoVim. If you use
anything else, your results may vary. Issues & PRs welcome.
