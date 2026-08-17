"""Regression tests for the global fact-type partial vector-index layout."""

import asyncio
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import Connection, create_engine, text

import hindsight_api
from hindsight_api.migrations import ensure_vector_extension, run_migrations, to_libpq_url

_EXPECTED = {"idx_mu_emb_world", "idx_mu_emb_experience", "idx_mu_emb_observation"}
_PARENT_REVISION = "c4f7a91b2d38"


@pytest.fixture(scope="module")
def vec_db_url():
    from hindsight_api.pg0 import EmbeddedPostgres

    pg0 = EmbeddedPostgres(name="hindsight-vecidx-test", port=5570)
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(pg0.ensure_running())
    finally:
        loop.close()


def _reset_schema(db_url: str, schema: str) -> None:
    engine = create_engine(db_url)
    try:
        with engine.connect() as conn:
            conn.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
            conn.commit()
    finally:
        engine.dispose()


def _vector_indexes(conn: Connection, schema: str) -> set[str]:
    return {
        row[0]
        for row in conn.execute(
            text(
                "SELECT indexname FROM pg_indexes "
                "WHERE schemaname = :schema AND tablename = 'memory_units' "
                "AND indexdef LIKE '%embedding%'"
            ),
            {"schema": schema},
        )
    }


def _alembic_config(db_url: str, schema: str) -> Config:
    cfg = Config()
    cfg.set_main_option("script_location", str(Path(hindsight_api.__file__).parent / "alembic"))
    cfg.set_main_option("sqlalchemy.url", to_libpq_url(db_url))
    cfg.set_main_option("path_separator", "os")
    cfg.set_main_option("target_schema", schema)
    return cfg


@pytest.mark.xdist_group("vecidx_pg0")
def test_migration_creates_three_global_fact_type_indexes(vec_db_url):
    schema = "vecidx_global_fresh"
    _reset_schema(vec_db_url, schema)
    run_migrations(vec_db_url, schema=schema)
    ensure_vector_extension(vec_db_url, vector_extension="pgvector", schema=schema)

    engine = create_engine(vec_db_url)
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text(
                    "SELECT indexname, indexdef FROM pg_indexes "
                    "WHERE schemaname = :schema AND tablename = 'memory_units' "
                    "AND indexname = ANY(:names)"
                ),
                {"schema": schema, "names": list(_EXPECTED)},
            ).fetchall()
            assert {row[0] for row in rows} == _EXPECTED
            assert all("WHERE (fact_type = '" in row[1] for row in rows)
            conn.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
            conn.commit()
    finally:
        engine.dispose()


@pytest.mark.xdist_group("vecidx_pg0")
def test_upgrade_replaces_legacy_global_and_per_bank_indexes(vec_db_url):
    schema = "vecidx_global_upgrade"
    _reset_schema(vec_db_url, schema)
    run_migrations(vec_db_url, schema=schema)
    cfg = _alembic_config(vec_db_url, schema)
    command.downgrade(cfg, _PARENT_REVISION)

    engine = create_engine(vec_db_url)
    try:
        with engine.connect() as conn:
            conn.execute(
                text(
                    f'CREATE INDEX idx_memory_units_embedding ON "{schema}".memory_units '
                    "USING hnsw (embedding vector_cosine_ops)"
                )
            )
            conn.execute(
                text(
                    f'CREATE INDEX idx_mu_emb_worl_deadbeef ON "{schema}".memory_units '
                    "USING hnsw (embedding vector_cosine_ops) "
                    "WHERE fact_type = 'world' AND bank_id = 'legacy'"
                )
            )
            conn.commit()

        command.upgrade(cfg, "heads")
        with engine.connect() as conn:
            assert _vector_indexes(conn, schema) == _EXPECTED
            conn.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
            conn.commit()
    finally:
        engine.dispose()


@pytest.mark.xdist_group("vecidx_pg0")
def test_empty_table_rebuilds_missing_global_index(vec_db_url):
    schema = "vecidx_global_empty_reconcile"
    _reset_schema(vec_db_url, schema)
    run_migrations(vec_db_url, schema=schema)
    engine = create_engine(vec_db_url)
    try:
        with engine.connect() as conn:
            conn.execute(text(f'DROP INDEX "{schema}".idx_mu_emb_world'))
            conn.commit()
        ensure_vector_extension(vec_db_url, vector_extension="pgvector", schema=schema)
        with engine.connect() as conn:
            assert _vector_indexes(conn, schema) == _EXPECTED
            conn.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
            conn.commit()
    finally:
        engine.dispose()


@pytest.mark.xdist_group("vecidx_pg0")
def test_populated_table_requires_explicit_concurrent_rebuild(vec_db_url):
    schema = "vecidx_global_populated_reconcile"
    _reset_schema(vec_db_url, schema)
    run_migrations(vec_db_url, schema=schema)
    engine = create_engine(vec_db_url)
    try:
        with engine.connect() as conn:
            conn.execute(text(f'DROP INDEX "{schema}".idx_mu_emb_world'))
            conn.execute(
                text(
                    f'INSERT INTO "{schema}".memory_units (bank_id, text, embedding, event_date) '
                    "VALUES ('bank', 'fact', CAST(:embedding AS vector), now())"
                ),
                {"embedding": "[" + ",".join(["0.1"] * 384) + "]"},
            )
            conn.commit()
        with pytest.raises(RuntimeError, match="vector-indexes --rebuild"):
            ensure_vector_extension(vec_db_url, vector_extension="pgvector", schema=schema)
        with engine.connect() as conn:
            conn.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
            conn.commit()
    finally:
        engine.dispose()
