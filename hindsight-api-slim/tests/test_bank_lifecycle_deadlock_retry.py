"""Bank lifecycle does not issue shared vector-index DDL."""

import uuid

import pytest
from asyncpg.exceptions import DeadlockDetectedError

from hindsight_api import RequestContext
from hindsight_api.engine.memory_engine import MemoryEngine
from hindsight_api.engine.retain import bank_utils


@pytest.mark.asyncio
async def test_bank_create_retries_transient_deadlock(
    memory: MemoryEngine, request_context: RequestContext, monkeypatch
):
    """A deadlock during the lazy bank-create tx retries the whole tx."""
    backend = await memory._get_backend()
    real = bank_utils.get_or_create_bank_profile_on_conn
    calls = 0

    async def flaky(conn, bank_id, *, ops):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise DeadlockDetectedError("deadlock detected")
        return await real(conn, bank_id, ops=ops)

    monkeypatch.setattr(bank_utils, "get_or_create_bank_profile_on_conn", flaky)

    bank_id = f"test-deadlock-{uuid.uuid4().hex[:8]}"
    try:
        result = await bank_utils.get_or_create_bank_profile(backend, bank_id)
        assert calls == 2, "expected exactly one retry after the injected deadlock"
        assert result.created is True
    finally:
        await memory.delete_bank(bank_id, request_context=request_context)
