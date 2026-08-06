"""CLI unit tests with mocked graph and prompts."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.cli import main as cli_main


def test_run_query_invokes_graph(monkeypatch: pytest.MonkeyPatch):
    graph = MagicMock()
    graph.invoke.return_value = {
        "answer": "ok",
        "intent": "conceptual",
        "confidence": -8.0,
    }
    monkeypatch.setattr(cli_main, "get_graph", lambda: graph)

    result = cli_main._run_query("qué es RICE?")
    assert result["answer"] == "ok"
    graph.invoke.assert_called_once()
    payload = graph.invoke.call_args.args[0]
    assert payload["question"] == "qué es RICE?"
    assert payload["attempts"] == 0


def test_main_exit_path(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    monkeypatch.setattr(cli_main.Prompt, "ask", lambda *_args, **_kwargs: "salir")
    monkeypatch.setattr(cli_main, "load_dotenv", lambda: None)

    cli_main.main()

    captured = capsys.readouterr()
    assert "PO Copilot" in captured.out
    assert "Hasta luego" in captured.out


def test_main_prints_answer(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    answers = iter(["qué es RICE?", "salir"])
    monkeypatch.setattr(cli_main.Prompt, "ask", lambda *_a, **_k: next(answers))
    monkeypatch.setattr(cli_main, "load_dotenv", lambda: None)
    monkeypatch.setattr(
        cli_main,
        "_run_query",
        lambda _q: {
            "answer": "RICE es un framework",
            "intent": "conceptual",
            "confidence": -8.1,
        },
    )

    cli_main.main()

    out = capsys.readouterr().out
    assert "intent=conceptual" in out
    assert "RICE es un framework" in out


def test_main_handles_errors(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    answers = iter(["boom", "salir"])
    monkeypatch.setattr(cli_main.Prompt, "ask", lambda *_a, **_k: next(answers))
    monkeypatch.setattr(cli_main, "load_dotenv", lambda: None)

    def _raise(_q: str):
        raise RuntimeError("ollama down")

    monkeypatch.setattr(cli_main, "_run_query", _raise)
    cli_main.main()

    out = capsys.readouterr().out
    assert "Error" in out
    assert "ollama down" in out
