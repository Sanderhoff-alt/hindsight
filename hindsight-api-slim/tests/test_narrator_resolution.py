"""Narrator injection and bank name decoupling.

The "Narrator: {name}" line in fact extraction is stamped into the who-dimension
of first-person facts when present. Bank profile ``name`` is a display/management
label (e.g. project name "AuditProject_0825" or routing key "my-agent::123"), NOT an
agent persona, and must not be injected as a Narrator by default.

These are pure unit tests — no LLM, no DB. They pin that the Narrator line is
present/absent accordingly.
"""

from datetime import datetime

from hindsight_api.engine.retain.fact_extraction import _build_user_message


class TestNarratorInjection:
    def _msg(self, agent_name, context="agent log"):
        return _build_user_message(
            chunk="I shipped the fix.",
            chunk_index=0,
            total_chunks=1,
            event_date=datetime(2024, 6, 1),
            context=context,
            metadata=None,
            agent_name=agent_name,
        )

    def test_no_narrator_line_by_default(self):
        """agent_name=None (the default retain case) → no Narrator line."""
        msg = self._msg(None)
        assert "Narrator:" not in msg

    def test_narrator_line_present_when_explicitly_supplied(self):
        """When an explicit agent_name is provided, Narrator line is injected."""
        msg = self._msg("Aria")
        assert "Narrator: Aria" in msg

    def test_context_precedence_clause_only_when_context_set(self):
        """The 'Context above takes precedence' clause appears only with a context."""
        with_context = self._msg("Aria", context="chat with a customer")
        assert "Context above takes precedence" in with_context

        without_context = self._msg("Aria", context="")
        assert "Narrator: Aria" in without_context  # base narrator still present
        assert "Context above takes precedence" not in without_context

    def test_project_or_routing_names_never_leak_when_unspecified(self):
        """Display names (e.g. AuditProject_0825, routing keys) never reach the prompt by default."""
        msg = self._msg(None, context="user interaction log")
        assert "Narrator:" not in msg
        assert "AuditProject_0825" not in msg
        assert "my-agent::channel-456::user-789" not in msg
