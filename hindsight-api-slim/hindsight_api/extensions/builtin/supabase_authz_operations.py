"""Supabase organization authz operation definitions."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal, TypedDict

OperationSource = Literal["bank_read", "bank_write", "special_bank", "unscoped"]
OperationScope = Literal["bank", "unscoped"]


class OperationDefinition(TypedDict, total=False):
    name: str
    source: OperationSource
    action: Literal["read", "write"]
    scope: OperationScope


BANK_READ_OPERATION_NAMES: tuple[str, ...] = (
    "get_bank_config",
    "get_bank_profile",
    "get_bank_stats",
    "list_directives",
    "get_directive",
    "get_memories_timeseries",
    "get_memory_unit",
    "list_memory_units",
    "list_observation_scopes",
    "get_observation_history",
    "list_tags",
    "get_document",
    "list_documents",
    "list_document_chunks",
    "get_chunk",
    "list_mental_models",
    "list_mental_model_tags",
    "list_entities",
    "get_entity",
    "get_entity_state",
    "get_entity_graph",
    "get_graph_data",
    "list_operations",
    "get_operation_status",
    "list_webhooks",
    "list_webhook_deliveries",
)

BANK_WRITE_OPERATION_NAMES: tuple[str, ...] = (
    "update_bank",
    "update_bank_config",
    "update_bank_disposition",
    "set_bank_mission",
    "merge_bank_mission",
    "reset_bank_config",
    "delete_bank",
    "create_directive",
    "update_directive",
    "delete_directive",
    "update_memory_unit",
    "submit_async_consolidation",
    "retry_failed_consolidation",
    "clear_observations",
    "clear_observations_for_memory",
    "update_document",
    "delete_document",
    "reprocess_document",
    "create_mental_model",
    "update_mental_model",
    "delete_mental_model",
    "clear_mental_model",
    "submit_async_graph_maintenance",
    "cancel_operation",
    "retry_operation",
    "create_webhook",
    "update_webhook",
    "delete_webhook",
)

SPECIAL_BANK_OPERATION_DEFINITIONS: tuple[OperationDefinition, ...] = (
    {"name": "recall", "source": "special_bank", "action": "read", "scope": "bank"},
    {"name": "reflect", "source": "special_bank", "action": "read", "scope": "bank"},
    {"name": "retain", "source": "special_bank", "action": "write", "scope": "bank"},
    {"name": "consolidate", "source": "special_bank", "action": "write", "scope": "bank"},
    {"name": "mental_model_get", "source": "special_bank", "action": "read", "scope": "bank"},
    {"name": "mental_model_refresh", "source": "special_bank", "action": "write", "scope": "bank"},
)

UNSCOPED_OPERATION_DEFINITIONS: tuple[OperationDefinition, ...] = (
    {"name": "create_bank", "source": "unscoped", "action": "write", "scope": "unscoped"},
)


def _definitions_for_source(
    names: tuple[str, ...], source: Literal["bank_read", "bank_write"], action: Literal["read", "write"]
) -> tuple[OperationDefinition, ...]:
    return tuple({"name": name, "source": source, "action": action, "scope": "bank"} for name in names)


@lru_cache(maxsize=1)
def load_operation_definitions() -> tuple[OperationDefinition, ...]:
    return (
        *_definitions_for_source(BANK_READ_OPERATION_NAMES, "bank_read", "read"),
        *_definitions_for_source(BANK_WRITE_OPERATION_NAMES, "bank_write", "write"),
        *SPECIAL_BANK_OPERATION_DEFINITIONS,
        *UNSCOPED_OPERATION_DEFINITIONS,
    )


def operation_names_for_source(source: OperationSource) -> frozenset[str]:
    return frozenset(operation["name"] for operation in load_operation_definitions() if operation["source"] == source)


def operation_names_for_scope(scope: OperationScope) -> frozenset[str]:
    return frozenset(operation["name"] for operation in load_operation_definitions() if operation["scope"] == scope)
