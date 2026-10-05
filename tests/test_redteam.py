"""Self-check for the red-team gate's fail-closed behaviour.

No server needed: httpx calls are replaced with fakes. Verifies the three
outcomes (breach / held / unreachable) map to the right exit codes.
"""
import importlib.util
import sys
from pathlib import Path

import httpx

_SPEC = importlib.util.spec_from_file_location(
    "redteam", Path(__file__).resolve().parent.parent / "security" / "redteam.py"
)
redteam = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(redteam)


def _resp(status, text="", json_body=None):
    request = httpx.Request("GET", "http://t")
    if json_body is not None:
        return httpx.Response(status, json=json_body, request=request)
    return httpx.Response(status, text=text, request=request)


def _run(monkeypatch, capsys, post, get):
    monkeypatch.setattr(redteam.httpx, "post", post)
    monkeypatch.setattr(redteam.httpx, "get", get)
    monkeypatch.setattr(sys, "argv", ["redteam.py", "--base-url", "http://t"])
    code = redteam.main()
    return code, capsys.readouterr().out


def _down(*a, **k):
    raise httpx.ConnectError("connection refused")


def _held_post(*a, **k):
    return _resp(401, "no")


def _held_get(url, **k):
    return _resp(401 if url.endswith("/admin/users") else 404, "nope")


def _breach_post(*a, **k):
    return _resp(200, json_body={"username": "admin"})


def test_all_held_passes(monkeypatch, capsys):
    code, out = _run(monkeypatch, capsys, _held_post, _held_get)
    assert code == 0
    assert "GATE: PASS" in out


def test_unreachable_target_fails_closed(monkeypatch, capsys):
    code, out = _run(monkeypatch, capsys, _down, _down)
    assert code == 2
    assert "GATE: FAIL - target unreachable" in out
    assert "GATE: PASS" not in out


def test_one_attack_unreachable_is_not_a_pass(monkeypatch, capsys):
    code, out = _run(monkeypatch, capsys, _down, _held_get)
    assert code == 2
    assert "GATE: FAIL - target unreachable" in out


def test_partial_secret_probe_failure_is_not_a_pass(monkeypatch, capsys):
    def flaky_get(url, **k):
        if url.endswith("/debug"):
            raise httpx.ReadTimeout("timeout")
        return _held_get(url)

    code, _ = _run(monkeypatch, capsys, _held_post, flaky_get)
    assert code == 2


def test_gateway_5xx_is_inconclusive_not_held(monkeypatch, capsys):
    def bad_gateway(*a, **k):
        return _resp(503, "bad gateway")

    code, out = _run(monkeypatch, capsys, bad_gateway, _held_get)
    assert code == 2
    assert "GATE: FAIL - target unreachable" in out


def test_breach_still_exits_1(monkeypatch, capsys):
    code, out = _run(monkeypatch, capsys, _breach_post, _held_get)
    assert code == 1
    assert "attack(s) succeeded" in out


def test_breach_takes_precedence_over_unreachable(monkeypatch, capsys):
    code, out = _run(monkeypatch, capsys, _breach_post, _down)
    assert code == 1
    assert "attack(s) succeeded" in out
    assert "target unreachable" in out
