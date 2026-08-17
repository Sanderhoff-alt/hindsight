"""Replace per-bank vector indexes with three global fact-type partial indexes.

The per-(bank, fact_type) layout makes PostgreSQL planning time grow with the
number of banks. A single partial index for each fact type keeps the catalog
small while still allowing the bank_id predicate to be applied during the ANN
scan. Unlike the old unfiltered global index, every recall arm retains its
fact_type predicate, so the ANN candidate set is limited to the requested
fact class. This migration is PostgreSQL-only; Oracle uses its existing
partitioned global vector index and does not support partial vector indexes.
"""

import os
from collections.abc import Sequence

from alembic import context, op
from sqlalchemy import text

from hindsight_api.alembic._dialect import run_for_dialect

revision: str = "b7e4d2a91f63"
down_revision: str | Sequence[str] | None = "c4f7a91b2d38"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_FACT_TYPES: tuple[str, ...] = ("world", "experience", "observation")


def _schema_prefix() -> str:
    schema = context.config.get_main_option("target_schema")
    return f'"{schema}".' if schema else ""


def _extension() -> str:
    ext = os.getenv("HINDSIGHT_API_VECTOR_EXTENSION", "pgvector").lower()
    if ext not in {"pgvector", "pgvectorscale", "vchord", "scann"}:
        raise ValueError(f"Invalid HINDSIGHT_API_VECTOR_EXTENSION: {ext}")
    return ext


def _using_clause(ext: str) -> str:
    if ext == "pgvectorscale":
        return "USING diskann (embedding vector_cosine_ops) WITH (num_neighbors = 50)"
    if ext == "vchord":
        return "USING vchordrq (embedding vector_cosine_ops)"
    return "USING hnsw (embedding vector_cosine_ops)"


def _pg_upgrade() -> None:
    ext = _extension()
    schema = _schema_prefix()
    bind = op.get_bind()
    schema_name = context.config.get_main_option("target_schema") or "public"

    # Remove every legacy per-bank index, the old fact-type indexes, and the
    # unfiltered global index before creating the canonical three indexes.
    rows = bind.execute(
        text(
            "SELECT indexname FROM pg_indexes "
            "WHERE schemaname = :schema_name AND tablename = 'memory_units' "
            "AND indexname LIKE 'idx_mu_emb_%' AND indexdef LIKE '%embedding%'"
        ),
        {"schema_name": schema_name},
    ).fetchall()
    # Index builds run outside the Alembic transaction so writes are not
    # blocked by a ShareLock on the shared memory_units table. A short lock
    # timeout intentionally fails startup fast when a concurrent DDL conflict
    # cannot be avoided; the next startup retries the idempotent migration.
    with context.get_context().autocommit_block():
        op.execute("SET lock_timeout = '10s'")
        try:
            for (index_name,) in rows:
                safe_name = str(index_name).replace('"', '""')
                op.execute(f'DROP INDEX CONCURRENTLY IF EXISTS {schema}"{safe_name}"')

            if ext == "scann":
                return

            op.execute(f"DROP INDEX CONCURRENTLY IF EXISTS {schema}idx_memory_units_embedding")
            for fact_type in _FACT_TYPES:
                index_name = f"idx_mu_emb_{fact_type}"
                op.execute(
                    f"CREATE INDEX CONCURRENTLY IF NOT EXISTS {index_name} ON {schema}memory_units "
                    f"{_using_clause(ext)} WHERE fact_type = '{fact_type}'"
                )
        finally:
            # SET is session-scoped because SET LOCAL cannot be used here.
            # Do not leak the migration's short timeout to later migrations.
            op.execute("RESET lock_timeout")


def _pg_downgrade() -> None:
    ext = _extension()
    schema = _schema_prefix()
    for fact_type in _FACT_TYPES:
        op.execute(f"DROP INDEX IF EXISTS {schema}idx_mu_emb_{fact_type}")

    if ext == "scann":
        return

    # Restore the previous per-bank layout for existing banks. New banks are
    # handled by the older runtime code after the downgrade.
    bind = op.get_bind()
    rows = bind.execute(text(f"SELECT bank_id, internal_id FROM {schema}banks")).fetchall()
    for bank_id, internal_id in rows:
        escaped_bank_id = str(bank_id).replace("'", "''")
        uid = str(internal_id).replace("-", "")[:16]
        for fact_type, suffix in (("world", "worl"), ("experience", "expr"), ("observation", "obsv")):
            op.execute(
                f"CREATE INDEX IF NOT EXISTS idx_mu_emb_{suffix}_{uid} ON {schema}memory_units "
                f"{_using_clause(ext)} WHERE fact_type = '{fact_type}' AND bank_id = '{escaped_bank_id}'"
            )


def upgrade() -> None:
    run_for_dialect(pg=_pg_upgrade)


def downgrade() -> None:
    run_for_dialect(pg=_pg_downgrade)
