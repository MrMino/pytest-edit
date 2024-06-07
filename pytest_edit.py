from __future__ import annotations

import os
import shutil
import subprocess

import pytest

DEFAULTS = {
    "posix": "vi",
    "nt": "notepad",
}


def choose_editor() -> str | None:
    user_editor = os.getenv("EDITOR")

    if user_editor is not None:
        return user_editor

    return DEFAULTS.get(os.name, None)


def no_lineno(path: str, _: int) -> list[str]:
    return [path]


def vi_style_linemark(path: str, lineno: int) -> list[str]:
    return [path, f"+{lineno}"]


def emacsclient_linemark(path: str, lineno: int) -> list[str]:
    return [f"+{lineno}:0", path]


def notepad_plus_plus_n_opt(path: str, lineno: int) -> list[str]:
    return [path, f"-n{lineno}"]


def vscode_goto(path: str, lineno: int) -> list[str]:
    return ["--goto", f"{path}:{lineno}:0"]


def pycharm_line_opt(path: str, lineno: int) -> list[str]:
    return ["--line", str(lineno), path]


OPT_GENERATOR = {
    "vi": vi_style_linemark,
    "vim": vi_style_linemark,
    "nvim": vi_style_linemark,
    "nano": vi_style_linemark,
    "gedit": vi_style_linemark,
    "emacsclient": emacsclient_linemark,
    "code": vscode_goto,
    "notepad": no_lineno,
    "notepad++": notepad_plus_plus_n_opt,
    "pycharm64": pycharm_line_opt,
    "pycharm": pycharm_line_opt,
}


def call_tty_child(argv):
    subprocess.call(argv)


def call_detached(argv):
    if os.name == "nt":
        subprocess.Popen(
            argv,
            creationflags=subprocess.DETACHED_PROCESS
            | subprocess.CREATE_NEW_PROCESS_GROUP,
        )
    else:
        subprocess.Popen(argv, start_new_session=True)


USES_TTY = {
    "vi": True,
    "vim": True,
    "nvim": True,
    "nano": True,
    "gedit": False,
    "emacsclient": True,
    "code": False,
    "notepad": False,
    "notepad++": False,
    "pycharm64": False,
    "pycharm": False,
}


def open_editor(path, lineno: int | None = None, editor: str | None = None) -> str:
    if editor is None:
        editor = choose_editor()

    if editor is None:
        raise RuntimeError("No 'editor' value given and no default available.")

    editor_name, _ = os.path.splitext(editor)
    if lineno is None:
        opts = [path]
    else:
        opt_generator = OPT_GENERATOR[editor_name]
        opts = opt_generator(path, lineno)

    exec_path = shutil.which(editor)
    assert isinstance(exec_path, str)

    argv = [exec_path] + opts
    call = call_tty_child if USES_TTY[editor_name] else call_detached

    call(argv)

    return editor


CACHE_KEY = f"{__name__}/failure_locations"
NOT_GIVEN = object()
NO_FAILED_TESTS_MSG = """\
No tests recorded as failed by pytest-edit.

If you just installed this plugin, rerun your tests to let it record the edit locations.
"""

@pytest.hookimpl
def pytest_addoption(parser):
    parser.addoption(
        "--edit",
        action="store",
        help=(
            "Open failed test in the editor specified via $EDITOR environment "
            "variable. Choose the test to open by specifying 'first', 'last', a "
            "number, or a test name. Omitting this will open the last failed test. "
            "A number will be interpretted as the index in the short summary "
            "list, for the test to open, starting from 0."
        ),
        default=NOT_GIVEN,
        nargs="?",
    )

@pytest.hookimpl
def pytest_sessionstart(session):
    edit_choice = session.config.option.edit

    if edit_choice is NOT_GIVEN:
        # User didn't specify the `--edit` flag.
        return

    failed = session.config.cache.get(CACHE_KEY, [])
    if not failed:
        pytest.exit(NO_FAILED_TESTS_MSG)
    
    if edit_choice is None:
        edit_choice = "last"

    if edit_choice == "last":
        edit_idx = -1
    elif edit_choice == "first":
        edit_idx = 0
    else:
        try:
            edit_idx = int(edit_choice)
        except ValueError:
            pytest.exit(
                f"Wrong value specified for --edit: {edit_choice!r} "
                f"Use either 'first', 'last', or a number."
            )

    try:
        path, lineno, nodeid = failed[edit_idx]
    except IndexError:
        pytest.exit(
            f"Test index specified for --edit is out of bounds: {edit_idx} "
            f"There are {len(failed)} failed tests."
        )

    # Editors count from 1, pytest counts lines from 0
    lineno += 1

    opened_editor = open_editor(path, lineno)
    pytest.exit(f"Opened {path} at {lineno} in editor {opened_editor!r}.", 0)


@pytest.hookimpl
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    if "failed" in terminalreporter.stats:
        failure_reports = terminalreporter.stats["failed"]

        # path, lineno, nodeid
        location_info = [report.location for report in failure_reports]
        config.cache.set(CACHE_KEY, location_info)

