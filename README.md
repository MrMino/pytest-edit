# pytest-edit

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/:pytest-edit)

A simple Pytest plugin for opening editor on the failed tests.

## Installation & usage

Install with:

```
pip install pytest-edit
```

**After installing the plugin, you need to rerun your tests before the plugin
will be able to open them for edition.**

Usage:

```
pytest --edit
```

This will open your `$EDITOR` at the first line of the last failed test. Not
all editors are capable of opening a file at a given line, and not all editors
that do are supported by `pytest-edit`. See below.

You can also specify the test using its index in the shortreport, for example:

```
pytest --edit=2    # will open the third failed test from the last run.
pytest --edit=-2   # will open the second-to-last failed test from the last run.
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

If an editor is not supported, the file of the specified test will be opened
without specifying the line the editor should place the cursor at.

**I have not tested 90% of the editor support** - there are at least 3
platforms with tens of different editors. Issues & PRs welcome.
