"""Check and rebuild migration-owned global vector indexes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .._vector_index import (
    FACT_TYPE_INDEXES,
    index_type_keyword,
    index_using_clause,
    is_global_fact_type_partial_index,
)


@dataclass
class SchemaVectorIndexResult:
    schema: str
    present: int = 0
    missing: int = 0
    unexpected: int = 0
    rebuilt: int = 0


def _expected_indexes(vector_extension: str) -> dict[str, str | None]:
    if vector_extension == "scann":
        return {"idx_memory_units_embedding": None}
    return FACT_TYPE_INDEXES


def _index_is_valid(row: Any, expected_fact_type: str | None, vector_extension: str) -> bool:
    indexdef = row["indexdef"].lower()
    if not row["indisvalid"] or not row["indisready"]:
        return False
    if index_type_keyword(vector_extension) not in indexdef:
        return False
    if vector_extension == "scann":
        return "embedding cosine" in indexdef
    return (
        "embedding vector_cosine_ops" in indexdef
        and expected_fact_type is not None
        and is_global_fact_type_partial_index(indexdef, expected_fact_type)
    )


async def _catalog_indexes(conn: Any, schema: str) -> list[Any]:
    return await conn.fetch(
        """
        SELECT c.relname AS indexname,
               pg_get_indexdef(i.indexrelid) AS indexdef,
               i.indisvalid,
               i.indisready
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        JOIN pg_index i ON i.indexrelid = c.oid
        JOIN pg_class t ON t.oid = i.indrelid
        WHERE n.nspname = $1 AND t.relname = 'memory_units'
          AND (c.relname LIKE 'idx_mu_emb_%' OR c.relname = 'idx_memory_units_embedding')
        """,
        schema,
    )


async def check_or_rebuild_vector_indexes(
    conn: Any,
    schemas: list[str],
    *,
    vector_extension: str,
    rebuild: bool,
) -> list[SchemaVectorIndexResult]:
    """Check or rebuild the global vector-index layout.

    PostgreSQL ANN indexes are rebuilt concurrently on a raw autocommit
    connection, so populated tables remain writable. ScaNN's supported build
    path is non-concurrent and may briefly block writes. Migrations still own
    the normal startup layout; this command is the explicit path for a backend
    switch on a live deployment.
    """
    expected = _expected_indexes(vector_extension)
    results: list[SchemaVectorIndexResult] = []
    for schema in schemas:
        rows = await _catalog_indexes(conn, schema)
        expected_rows = [row for row in rows if row["indexname"] in expected]
        valid = {
            row["indexname"]
            for row in expected_rows
            if _index_is_valid(row, expected[row["indexname"]], vector_extension)
        }
        unexpected = [row for row in rows if row["indexname"] not in expected]
        result = SchemaVectorIndexResult(schema=schema, present=len(valid))
        result.unexpected = len(unexpected)
        if valid == set(expected) and not unexpected:
            results.append(result)
            continue
        result.missing = len(set(expected) - valid)
        if not rebuild:
            results.append(result)
            continue

        invalid_expected = [row for row in expected_rows if row["indexname"] not in valid]
        indexes_to_drop = [*unexpected, *invalid_expected]
        safe_schema = schema.replace('"', '""')
        for row in indexes_to_drop:
            safe_index = row["indexname"].replace('"', '""')
            await conn.execute(f'DROP INDEX CONCURRENTLY IF EXISTS "{safe_schema}"."{safe_index}"')

        indexes_to_create = set(expected) - valid
        if vector_extension == "scann":
            if "idx_memory_units_embedding" in indexes_to_create:
                await conn.execute(
                    f'CREATE INDEX IF NOT EXISTS "idx_memory_units_embedding" '
                    f'ON "{safe_schema}".memory_units {index_using_clause(vector_extension)}'
                )
        else:
            for index_name, fact_type in FACT_TYPE_INDEXES.items():
                if index_name not in indexes_to_create:
                    continue
                await conn.execute(
                    f'CREATE INDEX CONCURRENTLY IF NOT EXISTS "{index_name}" '
                    f'ON "{safe_schema}".memory_units {index_using_clause(vector_extension)} '
                    f"WHERE fact_type = '{fact_type}'"
                )
        result.rebuilt = len(indexes_to_create)
        result.present = len(expected)
        result.missing = 0
        result.unexpected = 0
        results.append(result)
    return results
