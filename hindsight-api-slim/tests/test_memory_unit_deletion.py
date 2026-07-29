"""Authorization and public API coverage for hard memory-unit deletion."""

from __future__ import annotations

import asyncio
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, call, patch

import httpx
import pytest

from hindsight_api import RequestContext
from hindsight_api.api import create_app
from hindsight_api.engine.memory_engine import MemoryEngine
from hindsight_api.extensions import BankWriteOperation, OperationValidationError, ValidationResult
from hindsight_api.extensions.tenant import AuthenticationError, Tenant, TenantContext, TenantExtension
from hindsight_api.migrations import run_migrations


class _TwoSchemaTenantExtension(TenantExtension):
    """Resolve two API keys to distinct test-owned PostgreSQL schemas."""

    def __init__(self, schemas_by_api_key: dict[str, str]) -> None:
        super().__init__({})
        self._schemas_by_api_key = schemas_by_api_key

    async def authenticate(self, context: RequestContext) -> TenantContext:
        schema = self._schemas_by_api_key.get(context.api_key or "")
        if schema is None:
            raise AuthenticationError("invalid test tenant")
        return TenantContext(schema_name=schema)

    async def list_tenants(self) -> list[Tenant]:
        return [Tenant(schema=schema) for schema in self._schemas_by_api_key.values()]


async def _ensure_bank(memory: MemoryEngine, bank_id: str, request_context: RequestContext) -> None:
    await memory.get_bank_profile(bank_id=bank_id, request_context=request_context)


async def _insert_memory(
    memory: MemoryEngine,
    bank_id: str,
    *,
    fact_type: str = "experience",
    source_memory_ids: list[uuid.UUID] | None = None,
) -> uuid.UUID:
    memory_id = uuid.uuid4()
    pool = await memory._get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO memory_units (
                id, bank_id, text, fact_type, event_date, source_memory_ids,
                created_at, updated_at
            )
            VALUES ($1, $2, $3, $4, NOW(), $5, NOW(), NOW())
            """,
            memory_id,
            bank_id,
            f"memory-{memory_id}",
            fact_type,
            source_memory_ids,
        )
    return memory_id


async def _memory_exists(memory: MemoryEngine, memory_id: uuid.UUID) -> bool:
    pool = await memory._get_pool()
    async with pool.acquire() as conn:
        return bool(await conn.fetchval("SELECT EXISTS(SELECT 1 FROM memory_units WHERE id = $1)", memory_id))


def _validator(*, denied_bank: str | None = None) -> MagicMock:
    validator = MagicMock()
    validator.validate_bank_write = AsyncMock(
        side_effect=lambda ctx: (
            ValidationResult.reject("hard delete denied")
            if ctx.bank_id == denied_bank and ctx.operation is BankWriteOperation.DELETE_MEMORY_UNIT
            else ValidationResult.accept()
        )
    )
    return validator


@pytest.mark.asyncio
async def test_single_delete_authorizes_resolved_bank_before_mutation(
    memory: MemoryEngine, request_context: RequestContext
) -> None:
    bank_id = f"delete-single-{uuid.uuid4().hex[:8]}"
    await _ensure_bank(memory, bank_id, request_context)
    memory_id = await _insert_memory(memory, bank_id, fact_type="observation")
    validator = _validator()
    memory._operation_validator = validator

    result = await memory.delete_memory_unit(
        str(memory_id),
        bank_id=bank_id,
        request_context=request_context,
    )

    assert result.success is True
    assert result.unit_id == str(memory_id)
    assert not await _memory_exists(memory, memory_id)
    context = validator.validate_bank_write.await_args.args[0]
    assert context.bank_id == bank_id
    assert context.operation is BankWriteOperation.DELETE_MEMORY_UNIT
    assert context.request_context is request_context


@pytest.mark.asyncio
async def test_single_delete_denial_leaves_target_unchanged(
    memory: MemoryEngine, request_context: RequestContext
) -> None:
    bank_id = f"delete-denied-{uuid.uuid4().hex[:8]}"
    await _ensure_bank(memory, bank_id, request_context)
    memory_id = await _insert_memory(memory, bank_id, fact_type="observation")
    memory._operation_validator = _validator(denied_bank=bank_id)

    with pytest.raises(OperationValidationError, match="hard delete denied"):
        await memory.delete_memory_unit(str(memory_id), request_context=request_context)

    assert await _memory_exists(memory, memory_id)


@pytest.mark.asyncio
async def test_bulk_delete_authorizes_all_banks_before_any_mutation(
    memory: MemoryEngine, request_context: RequestContext
) -> None:
    allowed_bank = f"delete-allowed-{uuid.uuid4().hex[:8]}"
    denied_bank = f"delete-denied-{uuid.uuid4().hex[:8]}"
    for bank_id in (allowed_bank, denied_bank):
        await _ensure_bank(memory, bank_id, request_context)
    allowed_id = await _insert_memory(memory, allowed_bank, fact_type="observation")
    denied_id = await _insert_memory(memory, denied_bank, fact_type="observation")
    validator = _validator(denied_bank=denied_bank)
    memory._operation_validator = validator

    with pytest.raises(OperationValidationError, match="hard delete denied"):
        await memory.delete_memory_units(
            [str(allowed_id), str(denied_id)],
            request_context=request_context,
        )

    assert await _memory_exists(memory, allowed_id)
    assert await _memory_exists(memory, denied_id)
    validated_banks = [await_call.args[0].bank_id for await_call in validator.validate_bank_write.await_args_list]
    assert validated_banks == sorted([allowed_bank, denied_bank])


@pytest.mark.asyncio
async def test_bulk_delete_cascades_and_schedules_once_per_bank(
    memory: MemoryEngine, request_context: RequestContext
) -> None:
    bank_ids = [f"delete-cascade-{uuid.uuid4().hex[:8]}" for _ in range(2)]
    source_ids: list[uuid.UUID] = []
    survivor_ids: list[uuid.UUID] = []
    observation_ids: list[uuid.UUID] = []
    validator = _validator()
    pool = await memory._get_pool()
    for bank_id in bank_ids:
        await _ensure_bank(memory, bank_id, request_context)
        source_id = await _insert_memory(memory, bank_id)
        survivor_id = await _insert_memory(memory, bank_id)
        observation_id = await _insert_memory(
            memory,
            bank_id,
            fact_type="observation",
            source_memory_ids=[source_id],
        )
        source_ids.append(source_id)
        survivor_ids.append(survivor_id)
        observation_ids.append(observation_id)
        async with pool.acquire() as conn:
            entity_id = await conn.fetchval(
                "INSERT INTO entities (bank_id, canonical_name) VALUES ($1, $2) RETURNING id",
                bank_id,
                f"entity-{bank_id}",
            )
            await conn.execute(
                "INSERT INTO unit_entities (unit_id, entity_id) VALUES ($1, $2)",
                source_id,
                entity_id,
            )
            await conn.execute(
                """
                INSERT INTO memory_links (from_unit_id, to_unit_id, link_type, weight, bank_id)
                VALUES ($1, $2, 'temporal', 0.5, $3)
                """,
                source_id,
                survivor_id,
                bank_id,
            )
    memory._operation_validator = validator

    with (
        patch.object(
            memory._config_resolver,
            "resolve_full_config",
            new=AsyncMock(return_value=SimpleNamespace(enable_auto_consolidation=True)),
        ),
        patch.object(memory, "submit_async_consolidation", new=AsyncMock()) as submit_consolidation,
        patch.object(memory, "submit_async_graph_maintenance", new=AsyncMock()) as submit_graph_maintenance,
    ):
        result = await memory.delete_memory_units(
            [str(memory_id) for memory_id in source_ids],
            request_context=request_context,
        )

    assert result.deleted == 2
    assert set(result.per_bank) == set(bank_ids)
    assert all(counts.deleted == 1 for counts in result.per_bank.values())
    assert all(counts.invalidated_observations == 1 for counts in result.per_bank.values())
    assert not any([await _memory_exists(memory, memory_id) for memory_id in source_ids + observation_ids])
    async with pool.acquire() as conn:
        assert (
            await conn.fetchval(
                "SELECT COUNT(*) FROM unit_entities WHERE unit_id = ANY($1::uuid[])",
                source_ids,
            )
            == 0
        )
        assert (
            await conn.fetchval(
                """
                SELECT COUNT(*)
                FROM memory_links
                WHERE from_unit_id = ANY($1::uuid[]) OR to_unit_id = ANY($1::uuid[])
                """,
                source_ids,
            )
            == 0
        )
    assert all([await _memory_exists(memory, memory_id) for memory_id in survivor_ids])
    submit_consolidation.assert_has_awaits(
        [call(bank_id=bank_id, request_context=request_context) for bank_id in bank_ids],
        any_order=True,
    )
    submit_graph_maintenance.assert_has_awaits(
        [call(bank_id=bank_id, request_context=request_context) for bank_id in bank_ids],
        any_order=True,
    )
    assert submit_consolidation.await_count == len(bank_ids)
    assert submit_graph_maintenance.await_count == len(bank_ids)
    validated_banks = [await_call.args[0].bank_id for await_call in validator.validate_bank_write.await_args_list]
    assert validated_banks == sorted(bank_ids)


@pytest.mark.asyncio
async def test_bank_scoped_http_delete_rejects_cross_bank_ids(
    memory: MemoryEngine, request_context: RequestContext
) -> None:
    requested_bank = f"delete-http-{uuid.uuid4().hex[:8]}"
    other_bank = f"delete-http-other-{uuid.uuid4().hex[:8]}"
    for bank_id in (requested_bank, other_bank):
        await _ensure_bank(memory, bank_id, request_context)
    other_id = await _insert_memory(memory, other_bank, fact_type="observation")

    app = create_app(memory, initialize_memory=False)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        single_response = await client.delete(
            f"/v1/default/banks/{requested_bank}/memories/{other_id}",
        )
        bulk_response = await client.post(
            f"/v1/default/banks/{requested_bank}/memories/bulk-delete",
            json={"unit_ids": [str(other_id)]},
        )

    assert single_response.status_code == 400
    assert bulk_response.status_code == 400
    assert await _memory_exists(memory, other_id)


@pytest.mark.asyncio
async def test_http_single_and_bulk_delete_success(memory: MemoryEngine, request_context: RequestContext) -> None:
    bank_id = f"delete-http-success-{uuid.uuid4().hex[:8]}"
    await _ensure_bank(memory, bank_id, request_context)
    single_id = await _insert_memory(memory, bank_id, fact_type="observation")
    bulk_ids = [
        await _insert_memory(memory, bank_id, fact_type="observation"),
        await _insert_memory(memory, bank_id, fact_type="observation"),
    ]

    app = create_app(memory, initialize_memory=False)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        single_response = await client.delete(
            f"/v1/default/banks/{bank_id}/memories/{single_id}",
        )
        bulk_response = await client.post(
            f"/v1/default/banks/{bank_id}/memories/bulk-delete",
            json={"unit_ids": [str(memory_id) for memory_id in bulk_ids]},
        )
        missing_response = await client.delete(
            f"/v1/default/banks/{bank_id}/memories/{single_id}",
        )

    assert single_response.status_code == 200
    assert single_response.json() == {
        "success": True,
        "message": "Memory unit and all its links deleted successfully",
        "deleted_count": 1,
    }
    assert bulk_response.status_code == 200
    assert bulk_response.json() == {
        "success": True,
        "message": "Permanently deleted 2 memory units",
        "deleted_count": 2,
    }
    assert missing_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_memory_unit_isolated_to_authenticated_tenant_schema(
    memory: MemoryEngine,
    pg0_db_url: str,
) -> None:
    schema_a = f"delete_tenant_a_{uuid.uuid4().hex[:8]}"
    schema_b = f"delete_tenant_b_{uuid.uuid4().hex[:8]}"
    await asyncio.gather(
        asyncio.to_thread(run_migrations, pg0_db_url, schema=schema_a),
        asyncio.to_thread(run_migrations, pg0_db_url, schema=schema_b),
    )
    extension = _TwoSchemaTenantExtension({"key-a": schema_a, "key-b": schema_b})
    memory._tenant_extension = extension
    memory._config_resolver.tenant_extension = extension
    bank_id = "shared-bank"
    shared_memory_id = uuid.uuid4()

    try:
        for api_key, schema in (("key-a", schema_a), ("key-b", schema_b)):
            context = RequestContext(api_key=api_key)
            await _ensure_bank(memory, bank_id, context)
            pool = await memory._get_pool()
            async with pool.acquire() as conn:
                await conn.execute(
                    f"""
                    INSERT INTO "{schema}".memory_units (
                        id, bank_id, text, fact_type, event_date, created_at, updated_at
                    )
                    VALUES ($1, $2, $3, 'observation', NOW(), NOW(), NOW())
                    """,
                    shared_memory_id,
                    bank_id,
                    f"memory-for-{api_key}",
                )

        result = await memory.delete_memory_unit(
            str(shared_memory_id),
            bank_id=bank_id,
            request_context=RequestContext(api_key="key-a"),
        )

        assert result.success is True
        pool = await memory._get_pool()
        async with pool.acquire() as conn:
            exists_a = await conn.fetchval(
                f'SELECT EXISTS(SELECT 1 FROM "{schema_a}".memory_units WHERE id = $1)',
                shared_memory_id,
            )
            exists_b = await conn.fetchval(
                f'SELECT EXISTS(SELECT 1 FROM "{schema_b}".memory_units WHERE id = $1)',
                shared_memory_id,
            )
        assert exists_a is False
        assert exists_b is True
    finally:
        pool = await memory._get_pool()
        async with pool.acquire() as conn:
            await conn.execute(f'DROP SCHEMA IF EXISTS "{schema_a}" CASCADE')
            await conn.execute(f'DROP SCHEMA IF EXISTS "{schema_b}" CASCADE')
