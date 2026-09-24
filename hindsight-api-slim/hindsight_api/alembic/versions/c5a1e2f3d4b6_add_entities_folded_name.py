"""Add folded_name column to entities, replace lower index with folded_name index.

Revision ID: c5a1e2f3d4b6
Revises: d4f8b1c6e903
Create Date: 2026-09-24

Normalizes entity names for identity deduplication across script variants
(e.g., Traditional and Simplified Chinese like 用戶 vs 用户) and casing.
Stores the normalized key in `folded_name` while preserving original casing
and script in `canonical_name` for display.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import sqlalchemy as sa
from alembic import context, op

from hindsight_api.alembic._dialect import run_for_dialect
from hindsight_api.engine.retain.link_utils import fold_entity_name

revision: str = "c5a1e2f3d4b6"
down_revision: str | Sequence[str] | None = "d4f8b1c6e903"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_OLD_UNIQUE_INDEX = "idx_entities_bank_lower_name"
_NEW_UNIQUE_INDEX = "idx_entities_bank_folded_name"
_OLD_TRGM_INDEX = "entities_canonical_name_lower_trgm_nonlabel_idx"
_NEW_TRGM_INDEX = "entities_folded_name_trgm_nonlabel_idx"


@dataclass(slots=True)
class _EntityBackfillRow:
    id: str
    bank_id: str
    canonical_name: str
    mention_count: int
    first_seen: Any
    folded: str


def _pg_schema_prefix() -> str:
    """Schema-qualifier for raw SQL on PG (multi-tenant search_path)."""
    schema = context.config.get_main_option("target_schema")
    return f'"{schema}".' if schema else ""


def _backfill_folded_names(schema: str) -> None:
    """Backfill folded_name using Python's fold_entity_name for CJK and Unicode folding.

    Merges any pre-existing duplicate (bank_id, folded_name) rows if found.
    """
    bind = op.get_bind()
    rows = bind.execute(
        sa.text(f"SELECT id, bank_id, canonical_name, mention_count, first_seen FROM {schema}entities")
    ).fetchall()
    if not rows:
        return

    # Group by (bank_id, folded_name) to detect any pre-existing duplicates
    by_key: dict[tuple[str, str], list[_EntityBackfillRow]] = {}
    for r in rows:
        entity_id, bank_id, canonical_name, mention_count, first_seen = r[0], r[1], r[2], r[3], r[4]
        folded = fold_entity_name(canonical_name)
        key = (bank_id, folded)
        by_key.setdefault(key, []).append(
            _EntityBackfillRow(
                id=entity_id,
                bank_id=bank_id,
                canonical_name=canonical_name,
                mention_count=mention_count or 0,
                first_seen=first_seen,
                folded=folded,
            )
        )

    for (bank_id, folded), cluster in by_key.items():
        if len(cluster) == 1:
            item = cluster[0]
            bind.execute(
                sa.text(f"UPDATE {schema}entities SET folded_name = :folded WHERE id = :id AND bank_id = :bank_id"),
                {"folded": folded, "id": item.id, "bank_id": bank_id},
            )
        else:
            # Sort cluster: highest mention count first, earliest first_seen, stable id
            cluster.sort(key=lambda x: (-x.mention_count, str(x.first_seen or ""), str(x.id)))
            keeper = cluster[0]
            duplicates = cluster[1:]
            dup_ids = [d.id for d in duplicates]

            # Re-point unit_entities
            for dup_id in dup_ids:
                # Delete any unit_entities where keeper already links to the same unit
                bind.execute(
                    sa.text(
                        f"""
                        DELETE FROM {schema}unit_entities ue_dup
                        WHERE ue_dup.entity_id = :dup_id
                          AND EXISTS (
                              SELECT 1 FROM {schema}unit_entities ue_k
                              WHERE ue_k.unit_id = ue_dup.unit_id
                                AND ue_k.entity_id = :keeper_id
                          )
                        """
                    ),
                    {"dup_id": dup_id, "keeper_id": keeper.id},
                )
                bind.execute(
                    sa.text(f"UPDATE {schema}unit_entities SET entity_id = :keeper_id WHERE entity_id = :dup_id"),
                    {"keeper_id": keeper.id, "dup_id": dup_id},
                )
                # Re-point memory_links with bank_id scoping for multi-tenant isolation
                bind.execute(
                    sa.text(
                        f"UPDATE {schema}memory_links SET entity_id = :keeper_id WHERE entity_id = :dup_id AND bank_id = :bank_id"
                    ),
                    {"keeper_id": keeper.id, "dup_id": dup_id, "bank_id": bank_id},
                )
                # Delete duplicate entity rows
                bind.execute(
                    sa.text(f"DELETE FROM {schema}entities WHERE id = :dup_id AND bank_id = :bank_id"),
                    {"dup_id": dup_id, "bank_id": bank_id},
                )

            # Update keeper's folded_name
            bind.execute(
                sa.text(f"UPDATE {schema}entities SET folded_name = :folded WHERE id = :id AND bank_id = :bank_id"),
                {"folded": folded, "id": keeper.id, "bank_id": bank_id},
            )


def _pg_upgrade() -> None:
    bind = op.get_bind()
    schema = _pg_schema_prefix()
    target_schema = context.config.get_main_option("target_schema") or None

    op.execute(f"ALTER TABLE {schema}entities ADD COLUMN IF NOT EXISTS folded_name TEXT")

    # Trigger ensuring raw SQL inserts without folded_name (e.g. tests) default to LOWER(canonical_name)
    op.execute(
        f"""
        CREATE OR REPLACE FUNCTION {schema}set_entities_folded_name()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.folded_name IS NULL OR NEW.folded_name = '' THEN
                NEW.folded_name := LOWER(NEW.canonical_name);
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        f"""
        DROP TRIGGER IF EXISTS trg_entities_set_folded_name ON {schema}entities;
        CREATE TRIGGER trg_entities_set_folded_name
        BEFORE INSERT OR UPDATE OF canonical_name ON {schema}entities
        FOR EACH ROW
        EXECUTE FUNCTION {schema}set_entities_folded_name();
        """
    )

    _backfill_folded_names(schema)

    op.execute(f"ALTER TABLE {schema}entities ALTER COLUMN folded_name SET NOT NULL")

    with op.get_context().autocommit_block():
        # Clean up any leftover invalid indexes from aborted previous attempts
        for idx_name in (_NEW_UNIQUE_INDEX, _NEW_TRGM_INDEX):
            leftover_invalid = bind.execute(
                sa.text(
                    "SELECT NOT i.indisvalid "
                    "FROM pg_class c "
                    "JOIN pg_index i ON c.oid = i.indexrelid "
                    "JOIN pg_namespace n ON c.relnamespace = n.oid "
                    "WHERE c.relname = :index_name "
                    "  AND n.nspname = COALESCE(:target_schema, current_schema())"
                ),
                {"index_name": idx_name, "target_schema": target_schema},
            ).scalar()
            if leftover_invalid:
                op.execute(f"DROP INDEX CONCURRENTLY IF EXISTS {schema}{idx_name}")

        # Unique index on (bank_id, folded_name)
        op.execute(
            f"CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS {_NEW_UNIQUE_INDEX} "
            f"ON {schema}entities (bank_id, folded_name)"
        )
        op.execute(f"DROP INDEX CONCURRENTLY IF EXISTS {schema}{_OLD_UNIQUE_INDEX}")

    has_trgm = bind.execute(sa.text("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'pg_trgm')")).scalar()
    if has_trgm:
        with op.get_context().autocommit_block():
            # Build new trigram partial index on folded_name
            op.execute(
                f"CREATE INDEX CONCURRENTLY IF NOT EXISTS {_NEW_TRGM_INDEX} "
                f"ON {schema}entities USING GIN (folded_name gin_trgm_ops) "
                f"WHERE entity_kind != 'label'"
            )
            op.execute(f"DROP INDEX CONCURRENTLY IF EXISTS {schema}{_OLD_TRGM_INDEX}")


def _pg_downgrade() -> None:
    bind = op.get_bind()
    schema = _pg_schema_prefix()

    has_trgm = bind.execute(sa.text("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'pg_trgm')")).scalar()
    if has_trgm:
        with op.get_context().autocommit_block():
            op.execute(
                f"CREATE INDEX CONCURRENTLY IF NOT EXISTS {_OLD_TRGM_INDEX} "
                f"ON {schema}entities USING GIN (LOWER(canonical_name) gin_trgm_ops) "
                f"WHERE entity_kind != 'label'"
            )
            op.execute(f"DROP INDEX CONCURRENTLY IF EXISTS {schema}{_NEW_TRGM_INDEX}")

    with op.get_context().autocommit_block():
        op.execute(
            f"CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS {_OLD_UNIQUE_INDEX} "
            f"ON {schema}entities (bank_id, LOWER(canonical_name))"
        )
        op.execute(f"DROP INDEX CONCURRENTLY IF EXISTS {schema}{_NEW_UNIQUE_INDEX}")

    op.execute(f"DROP TRIGGER IF EXISTS trg_entities_set_folded_name ON {schema}entities")
    op.execute(f"DROP FUNCTION IF EXISTS {schema}set_entities_folded_name()")
    op.execute(f"ALTER TABLE {schema}entities DROP COLUMN IF EXISTS folded_name")


def _oracle_upgrade() -> None:
    op.execute(
        """
        BEGIN
            EXECUTE IMMEDIATE 'ALTER TABLE entities ADD (folded_name VARCHAR2(1000))';
        EXCEPTION WHEN OTHERS THEN
            IF SQLCODE != -1430 THEN RAISE; END IF;
        END;
        """
    )
    _backfill_folded_names("")
    op.execute(
        """
        BEGIN
            EXECUTE IMMEDIATE 'ALTER TABLE entities MODIFY (folded_name NOT NULL)';
        EXCEPTION WHEN OTHERS THEN
            NULL;
        END;
        """
    )
    op.execute(
        """
        BEGIN
            EXECUTE IMMEDIATE 'CREATE UNIQUE INDEX idx_entities_bank_folded_name ON entities (bank_id, folded_name)';
        EXCEPTION WHEN OTHERS THEN
            IF SQLCODE != -955 THEN RAISE; END IF;
        END;
        """
    )
    op.execute(
        """
        BEGIN
            EXECUTE IMMEDIATE 'DROP INDEX idx_ent_bank_lower_name';
        EXCEPTION WHEN OTHERS THEN
            IF SQLCODE != -1418 THEN RAISE; END IF;
        END;
        """
    )
    # Trigger ensuring raw SQL inserts without folded_name default to LOWER(canonical_name) on Oracle
    op.execute(
        """
        CREATE OR REPLACE TRIGGER trg_entities_folded_name_def
        BEFORE INSERT ON entities
        FOR EACH ROW
        BEGIN
            IF :NEW.folded_name IS NULL THEN
                :NEW.folded_name := LOWER(:NEW.canonical_name);
            END IF;
        END;
        """
    )


def _oracle_downgrade() -> None:
    op.execute(
        """
        BEGIN
            EXECUTE IMMEDIATE 'DROP TRIGGER trg_entities_folded_name_def';
        EXCEPTION WHEN OTHERS THEN
            IF SQLCODE != -4080 THEN RAISE; END IF;
        END;
        """
    )
    op.execute(
        """
        BEGIN
            EXECUTE IMMEDIATE 'CREATE UNIQUE INDEX idx_ent_bank_lower_name ON entities (bank_id, LOWER(canonical_name))';
        EXCEPTION WHEN OTHERS THEN
            IF SQLCODE != -955 THEN RAISE; END IF;
        END;
        """
    )
    op.execute(
        """
        BEGIN
            EXECUTE IMMEDIATE 'DROP INDEX idx_entities_bank_folded_name';
        EXCEPTION WHEN OTHERS THEN
            IF SQLCODE != -1418 THEN RAISE; END IF;
        END;
        """
    )
    op.execute(
        """
        BEGIN
            EXECUTE IMMEDIATE 'ALTER TABLE entities DROP COLUMN folded_name';
        EXCEPTION WHEN OTHERS THEN
            IF SQLCODE != -904 THEN RAISE; END IF;
        END;
        """
    )


def upgrade() -> None:
    run_for_dialect(pg=_pg_upgrade, oracle=_oracle_upgrade)


def downgrade() -> None:
    run_for_dialect(pg=_pg_downgrade, oracle=_oracle_downgrade)
