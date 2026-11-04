import json
import os

import desk
import pytest


@pytest.fixture
def desks(tmp_path):
    for d in ("datos", "teoria", "literatura"):
        (tmp_path / d).mkdir()
    return tmp_path


def lock(desks, name, pid):
    (desks / name / ".lock").write_text(json.dumps({"pid": pid, "encargo": "E.md", "started": "x"}))


def test_pid_alive():
    assert desk.pid_alive(os.getpid())
    assert not desk.pid_alive(0)
    assert not desk.pid_alive(2**22 + 12345)


def test_refuses_same_desk_twice_but_ignores_stale_locks(desks):
    lock(desks, "datos", os.getpid())
    with pytest.raises(desk.LaunchRefused, match="ya está trabajando"):
        desk.check_can_launch("datos", desks, free_gb=8)
    lock(desks, "datos", 2**22 + 12345)  # proceso muerto: lock obsoleto
    desk.check_can_launch("datos", desks, free_gb=8)


def test_refuses_above_max_concurrent(desks, monkeypatch):
    monkeypatch.setattr(desk, "MAX_CONCURRENT", 2)
    lock(desks, "datos", os.getpid())
    lock(desks, "teoria", os.getpid())
    with pytest.raises(desk.LaunchRefused, match="máximo 2"):
        desk.check_can_launch("literatura", desks, free_gb=8)


def test_refuses_low_memory_and_unknown_desk(desks):
    with pytest.raises(desk.LaunchRefused, match="GB libres"):
        desk.check_can_launch("datos", desks, free_gb=0.5)
    with pytest.raises(desk.LaunchRefused, match="no existe"):
        desk.check_can_launch("inventada", desks, free_gb=8)


def test_every_real_desk_has_a_tool_profile():
    real = {d.name for d in desk.DESKS.iterdir() if d.is_dir()}
    assert real <= set(desk.TOOLS), real - set(desk.TOOLS)
