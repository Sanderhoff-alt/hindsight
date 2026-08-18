"""Expose the mental model cron timezone to the maintenance routine.

The timezone remains part of the existing ``trigger`` JSON document; this
migration only updates the PostgreSQL discovery function so the scheduler can
read it. Missing values are returned as ``NULL`` and treated as UTC by the
application for backward compatibility.

The function is rebuilt with ``DROP FUNCTION`` + ``CREATE FUNCTION`` rather
than ``CREATE OR REPLACE FUNCTION`` because adding ``timezone`` changes the
``RETURNS TABLE`` signature, which PostgreSQL does not allow to be replaced.
The brief DROP/CREATE window is tolerated by the maintenance loop's existing
per-tick exception handling.

Its body is based on the latest ``mental_models_with_cron()`` implementation
from ``c8b4e2a71f95``. Keep the lock-timeout restoration and skip arms in sync
with that migration when changing this function: they prevent concurrent tenant
DDL from aborting the whole maintenance sweep.

PostgreSQL only: the maintenance loop is PostgreSQL-only, so the Oracle slot
is intentionally absent. The install-run gate ensures that the database-global
routine is rebuilt exactly once when migrations are run per tenant schema.
"""

from collections.abc import Sequence

from alembic import context, op

from hindsight_api.alembic._dialect import run_for_dialect
from hindsight_api.config import get_config

revision: str = "d4e5f6a7b8c9"
down_revision: str | Sequence[str] | None = "f2a7c9d4b168"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_LOCK_TIMEOUT = "250ms"

_SKIP_ARMS = """
                EXCEPTION
                    -- Schema or its tables vanished between the pg_class
                    -- snapshot and this query (tenant dropped or migrating).
                    WHEN undefined_table OR invalid_schema_name OR undefined_column THEN
                        CONTINUE;
                    -- Schema is mid-DDL and holds (or has queued) an
                    -- AccessExclusiveLock. Skip it rather than wait: waiting is
                    -- what closes the deadlock cycle. deadlock_detected is
                    -- belt-and-braces for a cycle formed before lock_timeout.
                    WHEN lock_not_available OR deadlock_detected THEN
                        CONTINUE;
"""


def _schema_prefix() -> str:
    schema = context.config.get_main_option("target_schema")
    return f'"{schema}".' if schema else ""


def _configured_schema() -> str:
    return get_config().database_schema or "public"


def _target_schema() -> str | None:
    return context.config.get_main_option("target_schema")


def _is_install_run() -> bool:
    target = _target_schema()
    return not target or target == _configured_schema()


def _create_function(*, include_timezone: bool) -> None:
    schema = _schema_prefix()
    columns = ["schema_name text", "bank_id text", "mental_model_id text", "refresh_cron text"]
    if include_timezone:
        columns.append("timezone text")
    columns.append("last_refreshed_at timestamptz")
    columns_sql = ", ".join(columns)
    timezone_select = "mm.trigger->>'timezone'," if include_timezone else ""
    op.execute(f"DROP FUNCTION IF EXISTS {schema}mental_models_with_cron()")
    op.execute(
        f"""
        CREATE FUNCTION {schema}mental_models_with_cron()
        RETURNS TABLE({columns_sql})
        LANGUAGE plpgsql STABLE
        AS $fn$
        DECLARE
            sch text;
            prev_lock_timeout text;
        BEGIN
            prev_lock_timeout := current_setting('lock_timeout');
            PERFORM set_config('lock_timeout', '{_LOCK_TIMEOUT}', true);
            FOR sch IN
                SELECT n.nspname
                FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE c.relname = 'mental_models' AND c.relkind = 'r'
            LOOP
                BEGIN
                    RETURN QUERY EXECUTE format($q$
                        SELECT %1$L::text, mm.bank_id::text, mm.id::text,
                               mm.trigger->>'refresh_cron', {timezone_select}
                               mm.last_refreshed_at
                        FROM %1$I.mental_models mm
                        WHERE COALESCE(mm.trigger->>'refresh_cron', '') <> ''
                          AND NOT EXISTS (
                              SELECT 1 FROM %1$I.async_operations o
                              WHERE o.bank_id = mm.bank_id
                                AND o.operation_type = 'refresh_mental_model'
                                AND o.status IN ('pending', 'processing')
                                AND o.task_payload->>'mental_model_id' = mm.id::text
                          )
                    $q$, sch);
{_SKIP_ARMS}                END;
            END LOOP;
            PERFORM set_config('lock_timeout', prev_lock_timeout, true);
        END;
        $fn$;
        """
    )


def _pg_upgrade() -> None:
    if not _is_install_run():
        return
    _create_function(include_timezone=True)


def _pg_downgrade() -> None:
    if not _is_install_run():
        return
    _create_function(include_timezone=False)


def upgrade() -> None:
    run_for_dialect(pg=_pg_upgrade)


def downgrade() -> None:
    run_for_dialect(pg=_pg_downgrade)
