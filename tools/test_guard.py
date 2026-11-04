"""Tests del hook .claude/hooks/guard.js: se ejecuta con node igual que lo hace Claude Code."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

GUARD = Path(__file__).resolve().parents[1] / ".claude" / "hooks" / "guard.js"
pytestmark = pytest.mark.skipif(shutil.which("node") is None, reason="node no disponible")


def hook(tool, cwd, **tool_input):
    ev = {"tool_name": tool, "tool_input": tool_input, "cwd": str(cwd)}
    r = subprocess.run(["node", str(GUARD)], input=json.dumps(ev), capture_output=True, text=True)
    return r.returncode


@pytest.mark.parametrize("p", ["datalake/raw/fred/x.parquet", "papers/p01/data/raw/a.csv",
                               r"C:\repo\papers\p01\data\holdout\h.csv"])
def test_writes_to_raw_and_holdout_are_blocked(tmp_path, p):
    assert hook("Write", tmp_path, file_path=p, content="x") == 2
    assert hook("Edit", tmp_path, file_path=p) == 2


def test_normal_writes_pass(tmp_path):
    assert hook("Write", tmp_path, file_path="papers/p01/data/clean/a.parquet") == 0
    assert hook("Edit", tmp_path, file_path="datalake/fetch/fred.py") == 0


def test_holdout_reads_blocked_until_opened(tmp_path):
    paper = tmp_path / "papers" / "p01"
    assert hook("Read", tmp_path, file_path="papers/p01/data/holdout/h.csv") == 2
    assert hook("Grep", tmp_path, pattern="x", path="papers/p01/data/holdout") == 2
    assert hook("Bash", tmp_path, command="head papers/p01/data/holdout/h.csv") == 2
    (paper / "audits").mkdir(parents=True)
    (paper / "audits" / "holdout_opened.md").write_text("abierto")
    assert hook("Read", tmp_path, file_path="papers/p01/data/holdout/h.csv") == 0
    assert hook("Bash", tmp_path, command="head papers/p01/data/holdout/h.csv") == 0


def test_raw_reads_are_allowed(tmp_path):
    assert hook("Read", tmp_path, file_path="datalake/raw/fred/meta.json") == 0


@pytest.mark.parametrize("cmd", ["git commit --no-verify -m x", "git commit -n -m x", "git commit -anm x",
                                 "git add . && git commit -m 'a' --no-verify",
                                 "git config core.hooksPath /dev/null", "git -c core.hooksPath=x commit -m y"])
def test_precommit_bypass_blocked(tmp_path, cmd):
    assert hook("Bash", tmp_path, command=cmd) == 2


@pytest.mark.parametrize("cmd", ["git commit -m 'no -n aquí'", "git commit -am 'mensaje'",
                                 "git config --get core.hooksPath", "uv run pytest -n 4",
                                 "git config core.hooksPath .githooks && git config --get core.hooksPath",
                                 "git commit -F - <<'EOF'\nTexto que menciona --no-verify y core.hooksPath\nEOF\n"])
def test_legit_commands_pass(tmp_path, cmd):
    assert hook("Bash", tmp_path, command=cmd) == 0
