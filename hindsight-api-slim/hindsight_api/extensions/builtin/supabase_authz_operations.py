"""Supabase organization authz operation definitions."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal, TypedDict

from hindsight_api.extensions.operation_validator import BankReadOperation, BankWriteOperation

OperationSource = Literal["bank_read", "bank_write", "special_bank", "unscoped"]
OperationScope = Literal["bank", "unscoped"]


class OperationDefinition(TypedDict, total=False):
    name: str
    source: OperationSource
    action: Literal["read", "write"]
    scope: OperationScope


_API_UNREACHABLE_READ_OPERATIONS = frozenset({BankReadOperation.GET_ENTITY_STATE})
_API_UNREACHABLE_WRITE_OPERATIONS = frozenset(
    {BankWriteOperation.RUN_CONSOLIDATION, BankWriteOperation.SET_BANK_MISSION}
)

# The validator hook enums are the source of truth. Only operations with no public
# API path are excluded from API-key grants.
BANK_READ_OPERATION_NAMES = tuple(
    operation.value for operation in BankReadOperation if operation not in _API_UNREACHABLE_READ_OPERATIONS
)
BANK_WRITE_OPERATION_NAMES = tuple(
    operation.value for operation in BankWriteOperation if operation not in _API_UNREACHABLE_WRITE_OPERATIONS
)

SPECIAL_BANK_OPERATION_DEFINITIONS: tuple[OperationDefinition, ...] = (
    {"name": "recall", "source": "special_bank", "action": "read", "scope": "bank"},
    {"name": "reflect", "source": "special_bank", "action": "read", "scope": "bank"},
    {"name": "retain", "source": "special_bank", "action": "write", "scope": "bank"},
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
