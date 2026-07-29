"""Tests for hard memory-unit deletion convenience methods."""

from unittest.mock import AsyncMock

from hindsight_client import Hindsight
from hindsight_client_api.models.delete_response import DeleteResponse


def _make_client() -> Hindsight:
    return Hindsight(base_url="http://localhost:8888")


async def test_adelete_memory_unit_delegates_to_generated_api() -> None:
    client = _make_client()
    expected = DeleteResponse(success=True, deleted_count=1, message="deleted")
    client._memory_api.delete_memory = AsyncMock(return_value=expected)

    result = await client.adelete_memory_unit("bank-id", "memory-id")

    assert result is expected
    client._memory_api.delete_memory.assert_awaited_once_with(
        "bank-id",
        "memory-id",
        _request_timeout=client._timeout,
    )


def test_delete_memory_unit_sync_wrapper() -> None:
    client = _make_client()
    expected = DeleteResponse(success=True, deleted_count=1, message="deleted")
    client._memory_api.delete_memory = AsyncMock(return_value=expected)

    result = client.delete_memory_unit("bank-id", "memory-id")

    assert result is expected


async def test_adelete_memory_units_builds_typed_request() -> None:
    client = _make_client()
    expected = DeleteResponse(success=True, deleted_count=2, message="deleted")
    client._memory_api.bulk_delete_memories = AsyncMock(return_value=expected)

    result = await client.adelete_memory_units("bank-id", ["memory-1", "memory-2"])

    assert result is expected
    request = client._memory_api.bulk_delete_memories.await_args.args[1]
    assert request.unit_ids == ["memory-1", "memory-2"]
    client._memory_api.bulk_delete_memories.assert_awaited_once_with(
        "bank-id",
        request,
        _request_timeout=client._timeout,
    )


def test_delete_memory_units_sync_wrapper() -> None:
    client = _make_client()
    expected = DeleteResponse(success=True, deleted_count=1, message="deleted")
    client._memory_api.bulk_delete_memories = AsyncMock(return_value=expected)

    result = client.delete_memory_units("bank-id", ["memory-id"])

    assert result is expected
