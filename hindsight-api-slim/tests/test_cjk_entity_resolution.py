"""
Tests for CJK Traditional-to-Simplified folding and entity resolution.
"""

from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from hindsight_api.engine.db.ops_oracle import OracleOps
from hindsight_api.engine.db.ops_postgresql import PostgreSQLOps
from hindsight_api.engine.entity_resolver import (
    EntityResolver,
    _tokens_are_compatible,
    trigram_similarity,
)
from hindsight_api.engine.retain.link_utils import fold_entity_name
from hindsight_api.engine.retain.types import ResolvedEntity


def test_fold_entity_name_cjk_traditional_to_simplified():
    """Verify fold_entity_name converts Traditional Chinese characters to Simplified."""
    assert fold_entity_name("用戶") == "用户"
    assert fold_entity_name("計算機科學") == "计算机科学"
    assert fold_entity_name("臺灣大學") == "台湾大学"
    assert fold_entity_name("蘋果公司") == "苹果公司"
    assert fold_entity_name("微軟") == "微软"
    # Already simplified remains unchanged
    assert fold_entity_name("用户") == "用户"
    assert fold_entity_name("人工智能") == "人工智能"


def test_fold_entity_name_whitespace_and_mixed_scripts():
    """Verify fold_entity_name trims whitespace, collapses inner spaces, and handles mixed scripts."""
    assert fold_entity_name("  Apple   Vision   Pro  ") == "apple vision pro"
    assert fold_entity_name("  iPhone  應用程式  ") == "iphone 应用程式"
    assert fold_entity_name("  ChatGPT 機器人 ") == "chatgpt 机器人"


def test_cjk_trigram_similarity():
    """Traditional and Simplified variants of the same name should yield trigram similarity 1.0."""
    assert trigram_similarity("用戶", "用户") == 1.0
    assert trigram_similarity("蘋果手機", "苹果手机") == 1.0
    assert trigram_similarity("機器學習", "机器学习") == 1.0
    assert trigram_similarity("iPhone 應用程式", "iphone 应用程式") == 1.0


def test_cjk_tokens_are_compatible():
    """Token compatibility check should treat Traditional and Simplified forms as compatible."""
    assert _tokens_are_compatible("用戶", "用户") is True
    assert _tokens_are_compatible("蘋果公司", "苹果公司") is True
    assert _tokens_are_compatible("人工 智慧", "人工 智能") is False


@pytest.mark.asyncio
async def test_cjk_intrabatch_clustering_merges_traditional_and_simplified():
    """Same-batch Traditional and Simplified mentions should merge into a single entity."""
    mock_ops = SimpleNamespace(
        bulk_insert_entities=AsyncMock(return_value={"用户": "entity-cjk-001"}),
        fetch_missing_entity_ids=AsyncMock(return_value=[]),
    )
    resolver = EntityResolver(pool=SimpleNamespace(ops=mock_ops), entity_lookup="full")

    # Mention 1 is Traditional Chinese, Mention 2 is Simplified Chinese
    entities_data = [
        {"text": "用戶", "nearby_entities": [], "resolve": True},
        {"text": "用户", "nearby_entities": [], "resolve": True},
    ]

    resolved = await resolver._resolve_from_candidates(
        conn=AsyncMock(),
        bank_id="bank-cjk",
        entities_data=entities_data,
        unit_event_date=datetime.now(UTC),
        all_candidates={},
        cooccurrence_map={},
    )

    # Both mentions must resolve to the same entity
    assert len(resolved) == 2
    assert resolved[0].entity_id == "entity-cjk-001"
    assert resolved[1].entity_id == "entity-cjk-001"
    assert resolved[0].canonical_name == resolved[1].canonical_name

    # bulk_insert_entities should only receive ONE group
    mock_ops.bulk_insert_entities.assert_called_once()
    call_args = mock_ops.bulk_insert_entities.call_args
    entity_names = call_args[0][3]
    entity_folded_names = call_args.kwargs.get("entity_folded_names")
    assert len(entity_names) == 1
    assert entity_folded_names == ["用户"]


@pytest.mark.asyncio
async def test_cjk_fuzzy_match_resolves_to_existing_candidate():
    """A Traditional Chinese mention should resolve to an existing Simplified candidate in DB."""
    existing_candidate_id = "user-existing-id"
    candidate_row = (existing_candidate_id, "用户", {}, datetime.now(UTC), 10)

    resolver = EntityResolver(pool=SimpleNamespace(ops=MagicMock()), entity_lookup="trigram")

    entities_data = [
        {"text": "用戶", "nearby_entities": [], "resolve": True},
    ]

    resolved = await resolver._resolve_from_candidates(
        conn=AsyncMock(),
        bank_id="bank-cjk",
        entities_data=entities_data,
        unit_event_date=datetime.now(UTC),
        all_candidates={"用戶": [candidate_row]},
        cooccurrence_map={},
    )

    assert len(resolved) == 1
    assert resolved[0].entity_id == existing_candidate_id
    assert resolved[0].canonical_name == "用户"


@pytest.mark.asyncio
async def test_postgresql_bulk_insert_passes_folded_names():
    """PostgreSQLOps.bulk_insert_entities uses folded_name and ON CONFLICT (bank_id, folded_name)."""
    conn = AsyncMock()
    conn.fetch = AsyncMock(
        return_value=[
            {"id": "id-1", "folded_name": "用户", "name_lower": "用戶"},
        ]
    )
    ops = PostgreSQLOps()

    res = await ops.bulk_insert_entities(
        conn=conn,
        table="hindsight.entities",
        bank_id="bank-1",
        entity_names=["用戶"],
        entity_dates=[None],
        entity_kinds=["regular"],
        entity_folded_names=["用户"],
    )

    assert res["用户"] == "id-1"
    assert res["用戶"] == "id-1"

    conn.fetch.assert_called_once()
    sql = conn.fetch.call_args.args[0]
    assert "ON CONFLICT (bank_id, folded_name)" in sql
    assert "folded_name" in sql
    folded_arg = conn.fetch.call_args.args[3]
    assert folded_arg == ["用户"]


@pytest.mark.asyncio
async def test_oracle_bulk_insert_passes_folded_names():
    """OracleOps.bulk_insert_entities uses folded_name and ON CONFLICT (bank_id, folded_name)."""
    conn = AsyncMock()
    conn.execute = AsyncMock()
    conn.fetchrow = AsyncMock(return_value={"id": "id-1", "folded_name": "用户", "name_lower": "用戶"})
    ops = OracleOps()

    res = await ops.bulk_insert_entities(
        conn=conn,
        table="entities",
        bank_id="bank-1",
        entity_names=["用戶"],
        entity_dates=[None],
        entity_kinds=["regular"],
        entity_folded_names=["用户"],
    )

    assert res["用户"] == "id-1"
    assert res["用戶"] == "id-1"

    conn.execute.assert_called_once()
    sql = conn.execute.call_args.args[0]
    assert "ON CONFLICT (bank_id, folded_name)" in sql
    assert "folded_name" in sql
    assert conn.execute.call_args.args[3] == "用户"
