"""Tests for global fact-type vector indexes and UNION ALL retrieval."""

import uuid
from datetime import datetime, timezone

import pytest

_GLOBAL_INDEXES = {"idx_mu_emb_world", "idx_mu_emb_experience", "idx_mu_emb_observation"}

pytestmark = pytest.mark.xdist_group("vector-index-health-pg0")

# ---------------------------------------------------------------------------
# Unit tests — no DB required
# ---------------------------------------------------------------------------


async def _get_global_vector_indexes(pool) -> list[str]:
    """Return the canonical global fact-type vector indexes."""
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT indexname
            FROM pg_indexes
            WHERE tablename = 'memory_units'
              AND indexname = ANY($1::text[])
            ORDER BY indexname
            """,
            list(_GLOBAL_INDEXES),
        )
    return [row["indexname"] for row in rows]


@pytest.mark.asyncio
async def test_retain_does_not_create_per_bank_vector_indexes(memory, request_context):
    """Creating a bank leaves the three migration-owned global indexes unchanged."""
    bank_id = f"test_hnsw_create_{uuid.uuid4().hex[:8]}"
    try:
        before = await _get_global_vector_indexes(memory._pool)
        await memory.retain_async(
            bank_id=bank_id,
            content="Alice is a software engineer.",
            request_context=request_context,
        )
        assert await _get_global_vector_indexes(memory._pool) == before
    finally:
        await memory.delete_bank(bank_id, request_context=request_context)


@pytest.mark.asyncio
async def test_delete_bank_keeps_global_vector_indexes(memory, request_context):
    """Deleting a bank must not drop indexes shared by other banks."""
    bank_id = f"test_hnsw_drop_{uuid.uuid4().hex[:8]}"

    await memory.retain_async(
        bank_id=bank_id,
        content="Bob is a data scientist.",
        request_context=request_context,
    )
    # Verify indexes exist before deletion
    indexes_before = await _get_global_vector_indexes(memory._pool)

    await memory.delete_bank(bank_id, request_context=request_context)

    assert await _get_global_vector_indexes(memory._pool) == indexes_before


@pytest.mark.asyncio
async def test_retain_idempotent_bank_creation(memory, request_context):
    """Retaining into the same bank twice does not create extra indexes."""
    bank_id = f"test_hnsw_idem_{uuid.uuid4().hex[:8]}"
    try:
        await memory.retain_async(
            bank_id=bank_id,
            content="Carol is a product manager.",
            request_context=request_context,
        )
        await memory.retain_async(
            bank_id=bank_id,
            content="Carol joined the company in 2022.",
            request_context=request_context,
        )
        assert set(await _get_global_vector_indexes(memory._pool)) == _GLOBAL_INDEXES
    finally:
        await memory.delete_bank(bank_id, request_context=request_context)


@pytest.mark.asyncio
async def test_retrieve_semantic_bm25_grouped_by_fact_type(memory, request_context):
    """Combined retrieval groups typed semantic and BM25 candidates by fact type."""
    from hindsight_api.engine.search.retrieval import retrieve_semantic_bm25_combined_sql

    bank_id = f"test_retrieval_{uuid.uuid4().hex[:8]}"
    try:
        await memory.retain_async(
            bank_id=bank_id,
            content=("Alice is a software engineer at TechCorp. She visited Paris in 2023 for a conference."),
            context="background",
            event_date=datetime(2023, 6, 1, tzinfo=timezone.utc),
            request_context=request_context,
        )

        query_emb = memory.embeddings.encode(["software engineer Alice"])
        query_emb_str = str(query_emb[0])

        fact_types = ["world", "experience"]
        async with memory._pool.acquire() as conn:
            results = await retrieve_semantic_bm25_combined_sql(
                conn=conn,
                query_emb_str=query_emb_str,
                query_text="software engineer Alice",
                bank_id=bank_id,
                fact_types=fact_types,
                limit=5,
            )

        # Must return an entry for every requested fact_type
        assert set(results.keys()) == set(fact_types)

        for ft, result in results.items():
            # Semantic and BM25 lists must be lists
            assert isinstance(result.semantic, list)
            assert isinstance(result.bm25, list)
            # All semantic results must declare the correct fact_type
            for r in result.semantic:
                assert r.fact_type == ft, f"Semantic result has wrong fact_type: {r.fact_type}"
            # All BM25 results must declare the correct fact_type
            for r in result.bm25:
                assert r.fact_type == ft, f"BM25 result has wrong fact_type: {r.fact_type}"

    finally:
        await memory.delete_bank(bank_id, request_context=request_context)


@pytest.mark.asyncio
async def test_fetch_unit_dates_ignores_noncanonical_uuid_inputs(memory, request_context):
    """The indexed UUID lookup preserves the old text-comparison input behavior."""
    from hindsight_api.engine.db.ops_postgresql import PostgreSQLOps

    bank_id = f"test_unit_dates_{uuid.uuid4().hex[:8]}"
    try:
        await memory.retain_async(
            bank_id=bank_id,
            content="Alice joined TechCorp in 2023.",
            request_context=request_context,
        )

        async with memory._pool.acquire() as conn:
            unit_id = await conn.fetchval(
                "SELECT id::text FROM memory_units WHERE bank_id = $1 ORDER BY created_at LIMIT 1",
                bank_id,
            )
            rows = await PostgreSQLOps().fetch_unit_dates(
                conn,
                "memory_units",
                [unit_id, "not-a-uuid", unit_id.upper(), unit_id.replace("-", "")],
            )

        assert [str(row["id"]) for row in rows] == [unit_id]
    finally:
        await memory.delete_bank(bank_id, request_context=request_context)


@pytest.mark.asyncio
async def test_recall_reuses_semantic_pool_for_graph_seeds(memory, request_context, monkeypatch):
    """Default recall must not issue a second ANN query for graph entry points."""
    from hindsight_api.engine.search import link_expansion_retrieval

    async def fail_find_semantic_seeds(*args, **kwargs):
        raise AssertionError("default recall should reuse the combined semantic candidate pool")

    bank_id = f"test_graph_seed_reuse_{uuid.uuid4().hex[:8]}"
    try:
        await memory.retain_async(
            bank_id=bank_id,
            content="Alice is a software engineer at TechCorp.",
            request_context=request_context,
        )
        monkeypatch.setattr(link_expansion_retrieval, "_find_semantic_seeds", fail_find_semantic_seeds)

        result = await memory.recall_async(
            bank_id=bank_id,
            query="Where does Alice work?",
            fact_type=["world"],
            request_context=request_context,
        )

        assert result.results
    finally:
        await memory.delete_bank(bank_id, request_context=request_context)


@pytest.mark.asyncio
async def test_recall_keeps_graph_seed_query_for_stricter_semantic_floor(memory, request_context, monkeypatch):
    """A semantic floor above the graph floor must retain the dedicated seed query."""
    from hindsight_api.engine.response_models import MinScores
    from hindsight_api.engine.search import link_expansion_retrieval

    original_find_semantic_seeds = link_expansion_retrieval._find_semantic_seeds
    graph_seed_fact_types: list[str] = []

    async def record_find_semantic_seeds(*args, **kwargs):
        graph_seed_fact_types.append(args[3])
        return await original_find_semantic_seeds(*args, **kwargs)

    bank_id = f"test_graph_seed_fallback_{uuid.uuid4().hex[:8]}"
    try:
        await memory.retain_async(
            bank_id=bank_id,
            content="Alice is a software engineer at TechCorp.",
            request_context=request_context,
        )
        monkeypatch.setattr(link_expansion_retrieval, "_find_semantic_seeds", record_find_semantic_seeds)

        await memory.recall_async(
            bank_id=bank_id,
            query="Where does Alice work?",
            fact_type=["world"],
            min_scores=MinScores(semantic=0.9),
            request_context=request_context,
        )

        assert graph_seed_fact_types == ["world"]
    finally:
        await memory.delete_bank(bank_id, request_context=request_context)
