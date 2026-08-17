"""Bank creation does not perform vector-index DDL."""

from contextlib import asynccontextmanager

import pytest

from hindsight_api.engine.retain import bank_utils


class _FakeTransaction:
    def __init__(self, conn):
        self.conn = conn

    async def __aenter__(self):
        self.conn.in_transaction = True

    async def __aexit__(self, exc_type, exc, tb):
        if exc_type is None:
            self.conn.committed_bank = self.conn.pending_bank
        self.conn.pending_bank = None
        self.conn.in_transaction = False


class _FakeConnection:
    def __init__(self):
        self.committed_bank = None
        self.pending_bank = None
        self.in_transaction = False

    def transaction(self):
        return _FakeTransaction(self)

    async def fetchrow(self, query, bank_id):
        visible = self.pending_bank if self.in_transaction else self.committed_bank
        if visible != bank_id:
            return None
        return {"name": bank_id, "disposition": bank_utils.DEFAULT_DISPOSITION, "mission": ""}

    async def fetchval(self, query, bank_id, *args):
        if self.in_transaction:
            self.pending_bank = bank_id
        else:
            self.committed_bank = bank_id
        return bank_id


class _FakePool:
    def __init__(self, conn):
        self.conn = conn
        self.ops = None


@pytest.mark.asyncio
async def test_lazy_bank_create_does_not_call_vector_index_ddl(monkeypatch):
    conn = _FakeConnection()
    pool = _FakePool(conn)

    @asynccontextmanager
    async def acquire(*args, **kwargs):
        yield conn

    monkeypatch.setattr(bank_utils, "acquire_with_retry", acquire)
    result = await bank_utils.get_or_create_bank_profile(pool, "global-index-bank")
    assert result.created is True
    assert await bank_utils.get_bank_profile_if_exists(pool, "global-index-bank") is not None
