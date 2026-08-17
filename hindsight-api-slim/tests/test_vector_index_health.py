"""Regression tests for the migration-owned global vector-index check."""

import pytest
import asyncpg
from typer.testing import CliRunner

from hindsight_api.admin import cli
from hindsight_api.admin.cli import _run_vector_index_check
from hindsight_api.engine.vector_index_health import check_or_rebuild_vector_indexes

_TEST_SCHEMA = "public"
_EXPECTED = {"idx_mu_emb_world", "idx_mu_emb_experience", "idx_mu_emb_observation"}

pytestmark = pytest.mark.xdist_group("vector-index-health-pg0")


class _CatalogConn:
    def __init__(self, rows):
        self.rows = rows
        self.commands = []

    async def fetch(self, *args):
        return self.rows

    async def execute(self, query):
        self.commands.append(query)


@pytest.mark.asyncio
async def test_global_index_check_rejects_wrong_shape():
    conn = _CatalogConn(
        [
            {
                "indexname": "idx_mu_emb_world",
                "indexdef": "CREATE INDEX idx_mu_emb_world ON memory_units USING btree (bank_id)",
                "indisvalid": True,
                "indisready": True,
            }
        ]
    )

    result = (await check_or_rebuild_vector_indexes(conn, ["public"], vector_extension="pgvector", rebuild=False))[0]
    assert result.present == 0
    assert result.missing == 3


@pytest.mark.asyncio
async def test_scann_index_check_uses_unfiltered_global_index():
    conn = _CatalogConn(
        [
            {
                "indexname": "idx_memory_units_embedding",
                "indexdef": "CREATE INDEX idx_memory_units_embedding ON memory_units USING scann (embedding cosine)",
                "indisvalid": True,
                "indisready": True,
            }
        ]
    )

    result = (await check_or_rebuild_vector_indexes(conn, ["public"], vector_extension="scann", rebuild=False))[0]
    assert result.present == 1
    assert result.missing == 0


@pytest.mark.asyncio
async def test_global_index_check_reports_unexpected_legacy_indexes():
    rows = [
        {
            "indexname": name,
            "indexdef": f"CREATE INDEX {name} ON memory_units USING hnsw "
            f"(embedding vector_cosine_ops) WHERE fact_type = '{fact_type}'",
            "indisvalid": True,
            "indisready": True,
        }
        for name, fact_type in (
            ("idx_mu_emb_world", "world"),
            ("idx_mu_emb_experience", "experience"),
            ("idx_mu_emb_observation", "observation"),
        )
    ]
    rows.append(
        {
            "indexname": "idx_mu_emb_world_legacy",
            "indexdef": "CREATE INDEX idx_mu_emb_world_legacy ON memory_units USING hnsw",
            "indisvalid": True,
            "indisready": True,
        }
    )

    result = (
        await check_or_rebuild_vector_indexes(
            _CatalogConn(rows), ["public"], vector_extension="pgvector", rebuild=False
        )
    )[0]
    assert result.present == 3
    assert result.missing == 0
    assert result.unexpected == 1


@pytest.mark.asyncio
async def test_rebuild_uses_concurrent_global_index_ddl():
    conn = _CatalogConn(
        [
            {
                "indexname": "idx_mu_emb_world",
                "indexdef": "CREATE INDEX idx_mu_emb_world ON memory_units USING hnsw (bank_id)",
                "indisvalid": True,
                "indisready": True,
            }
        ]
    )

    result = (await check_or_rebuild_vector_indexes(conn, ["public"], vector_extension="pgvector", rebuild=True))[0]
    assert result.rebuilt == 3
    assert any("DROP INDEX CONCURRENTLY" in command for command in conn.commands)
    assert sum("CREATE INDEX CONCURRENTLY" in command for command in conn.commands) == 3


@pytest.mark.asyncio
async def test_vector_index_check_reports_global_indexes(pg0_db_url):
    results = await _run_vector_index_check(
        pg0_db_url,
        base_schema=_TEST_SCHEMA,
        schema=_TEST_SCHEMA,
        vector_extension="pgvector",
        rebuild=False,
    )
    assert len(results) == 1
    assert results[0].present == len(_EXPECTED)
    assert results[0].missing == 0


@pytest.mark.asyncio
async def test_vector_index_command_rebuilds_missing_indexes(pg0_db_url):
    conn = await asyncpg.connect(pg0_db_url)
    try:
        await conn.execute("DROP INDEX IF EXISTS public.idx_mu_emb_world")
    finally:
        await conn.close()

    results = await _run_vector_index_check(
        pg0_db_url,
        base_schema=_TEST_SCHEMA,
        schema=_TEST_SCHEMA,
        vector_extension="pgvector",
        rebuild=True,
    )
    assert results[0].rebuilt == 1
    assert results[0].missing == 0


@pytest.mark.asyncio
async def test_vector_index_command_rebuilds_populated_table(pg0_db_url):
    conn = await asyncpg.connect(pg0_db_url)
    try:
        await conn.execute("DROP INDEX IF EXISTS public.idx_mu_emb_world")
        await conn.execute(
            """
            INSERT INTO public.memory_units (bank_id, text, embedding, event_date)
            VALUES ('vector-health-rebuild', 'fact', $1::vector, now())
            """,
            "[" + ",".join(["0.1"] * 384) + "]",
        )
    finally:
        await conn.close()

    try:
        results = await _run_vector_index_check(
            pg0_db_url,
            base_schema=_TEST_SCHEMA,
            schema=_TEST_SCHEMA,
            vector_extension="pgvector",
            rebuild=True,
        )
        assert results[0].rebuilt == 1
        assert results[0].missing == 0
    finally:
        cleanup = await asyncpg.connect(pg0_db_url)
        try:
            await cleanup.execute("DELETE FROM public.memory_units WHERE bank_id = 'vector-health-rebuild'")
        finally:
            await cleanup.close()


def test_vector_index_command_has_explicit_rebuild_flag():
    runner = CliRunner()
    result = runner.invoke(cli.app, ["vector-indexes", "--help"])
    assert result.exit_code == 0, result.output
    assert "--rebuild" in result.output
