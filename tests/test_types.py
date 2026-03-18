# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

"""Tests for langchat.types — ChatResponse dataclass."""

from langchat.types import ChatResponse


def _make_response(**overrides) -> ChatResponse:
    return ChatResponse(
        text=overrides.get("text", "Hello!"),
        user_id=overrides.get("user_id", "alice"),
        domain=overrides.get("domain", "default"),
        status=overrides.get("status", "success"),
        response_time=overrides.get("response_time", 1.23),
        timestamp=overrides.get("timestamp", "2025-01-01T00:00:00Z"),
        error=overrides.get("error"),
    )


# ---------------------------------------------------------------------------
# Field access
# ---------------------------------------------------------------------------


class TestChatResponseFields:
    def test_text_field(self):
        r = _make_response(text="The answer is 42.")
        assert r.text == "The answer is 42."

    def test_user_id_field(self):
        r = _make_response(user_id="bob")
        assert r.user_id == "bob"

    def test_domain_field(self):
        r = _make_response(domain="science")
        assert r.domain == "science"

    def test_status_success(self):
        r = _make_response(status="success")
        assert r.status == "success"

    def test_status_error(self):
        r = _make_response(status="error")
        assert r.status == "error"

    def test_response_time_field(self):
        r = _make_response(response_time=0.75)
        assert r.response_time == 0.75

    def test_timestamp_field(self):
        r = _make_response(timestamp="2025-06-15T10:30:00Z")
        assert r.timestamp == "2025-06-15T10:30:00Z"

    def test_error_defaults_to_none(self):
        r = _make_response()
        assert r.error is None

    def test_error_carries_message(self):
        r = _make_response(status="error", error="LLM timeout")
        assert r.error == "LLM timeout"


# ---------------------------------------------------------------------------
# __bool__
# ---------------------------------------------------------------------------


class TestChatResponseBool:
    def test_true_when_success(self):
        r = _make_response(status="success")
        assert bool(r) is True

    def test_false_when_error(self):
        r = _make_response(status="error")
        assert bool(r) is False

    def test_usable_in_if_statement(self):
        r = _make_response(status="success")
        result = "ok" if r else "fail"
        assert result == "ok"

    def test_usable_in_assert(self):
        r = _make_response(status="success")
        assert r  # should not raise


# ---------------------------------------------------------------------------
# __str__
# ---------------------------------------------------------------------------


class TestChatResponseStr:
    def test_str_returns_text(self):
        r = _make_response(text="The sky is blue.")
        assert str(r) == "The sky is blue."

    def test_str_empty_text(self):
        r = _make_response(text="")
        assert str(r) == ""

    def test_print_compatible(self, capsys):
        r = _make_response(text="Printed!")
        print(r)
        captured = capsys.readouterr()
        assert "Printed!" in captured.out


# ---------------------------------------------------------------------------
# Dataclass behaviour
# ---------------------------------------------------------------------------


class TestChatResponseDataclass:
    def test_is_dataclass(self):
        import dataclasses

        assert dataclasses.is_dataclass(ChatResponse)

    def test_equality(self):
        r1 = _make_response()
        r2 = _make_response()
        assert r1 == r2

    def test_inequality_on_text(self):
        r1 = _make_response(text="A")
        r2 = _make_response(text="B")
        assert r1 != r2

    def test_repr_contains_class_name(self):
        r = _make_response()
        assert "ChatResponse" in repr(r)

    def test_fields_are_accessible_by_name(self):
        r = _make_response(text="hi", user_id="u", domain="d")
        assert r.text == "hi"
        assert r.user_id == "u"
        assert r.domain == "d"


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------


def test_chat_response_in_all():
    from langchat import types

    assert "ChatResponse" in types.__all__


def test_chat_response_importable_from_langchat():
    from langchat import ChatResponse as CR

    assert CR is ChatResponse
