"""Supabase organization-based authn/authz extensions for Cloud-like deployments."""

from __future__ import annotations

import asyncio
import hashlib
import logging
import re
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal

import httpx
import jwt as pyjwt
from jwt import PyJWK
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, field_validator

from hindsight_api.extensions.operation_validator import (
    BankListContext,
    BankListResult,
    BankReadContext,
    BankWriteContext,
    OperationValidatorExtension,
    RecallContext,
    ReflectContext,
    RetainContext,
    ValidationResult,
)
from hindsight_api.extensions.tenant import AuthenticationError, Tenant, TenantContext, TenantExtension
from hindsight_api.models import RequestContext

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT_SECONDS = 10.0
JWKS_CACHE_TTL_SECONDS = 600
JWKS_MIN_REFRESH_INTERVAL_SECONDS = 30
SUPPORTED_ALGORITHMS = ["RS256", "ES256"]
MIN_TOKEN_LENGTH = 20

_UUID_OR_SLUG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$")
_JWT_SHAPE_RE = re.compile(r"^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$")
_SCHEMA_PREFIX_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")

BANK_READ_OPERATIONS = frozenset(
    {
        "get_bank_config",
        "get_bank_profile",
        "get_bank_stats",
        "get_chunk",
        "get_directive",
        "get_document",
        "get_entity",
        "get_entity_graph",
        "get_entity_state",
        "get_graph_data",
        "get_memories_timeseries",
        "get_memory_unit",
        "get_observation_history",
        "get_operation_status",
        "list_directives",
        "list_document_chunks",
        "list_documents",
        "list_entities",
        "list_memory_units",
        "list_mental_models",
        "list_mental_model_tags",
        "list_observation_scopes",
        "list_operations",
        "list_tags",
        "list_webhook_deliveries",
        "list_webhooks",
        "recall",
        "reflect",
    }
)

BANK_WRITE_OPERATIONS = frozenset(
    {
        "cancel_operation",
        "clear_mental_model",
        "clear_observations",
        "clear_observations_for_memory",
        "create_directive",
        "create_mental_model",
        "create_webhook",
        "delete_bank",
        "delete_directive",
        "delete_document",
        "delete_mental_model",
        "delete_webhook",
        "merge_bank_mission",
        "reprocess_document",
        "reset_bank_config",
        "retry_operation",
        "retry_failed_consolidation",
        "run_consolidation",
        "set_bank_mission",
        "submit_async_consolidation",
        "submit_async_graph_maintenance",
        "update_bank",
        "update_bank_config",
        "update_bank_disposition",
        "update_directive",
        "update_document",
        "update_memory_unit",
        "update_mental_model",
        "update_webhook",
        "retain",
    }
)

ALL_BANK_OPERATIONS = BANK_READ_OPERATIONS | BANK_WRITE_OPERATIONS
MEMBER_BANK_OPERATIONS = BANK_READ_OPERATIONS | frozenset(
    {
        "create_mental_model",
        "retain",
        "update_document",
        "update_memory_unit",
        "update_mental_model",
    }
)


class OrganizationRow(BaseModel):
    """Organization row returned by Supabase PostgREST."""

    model_config = ConfigDict(extra="ignore")

    id: str
    name: str | None = None
    config: dict[str, Any] = Field(default_factory=dict)


class MemberRow(BaseModel):
    """Organization membership row returned by Supabase PostgREST."""

    model_config = ConfigDict(extra="ignore")

    org_id: str
    user_id: str
    role: Literal["owner", "admin", "member"]


class ApiKeyRow(BaseModel):
    """Hindsight scoped API key row returned by Supabase PostgREST."""

    model_config = ConfigDict(extra="ignore")

    id: str
    org_id: str
    created_by_user_id: str | None = None
    role: Literal["owner", "admin", "member"] = "member"
    allowed_operations: list[str] | None = None
    bank_scope_mode: Literal["all", "selected"] = "all"
    revoked_at: str | None = None
    expires_at: str | None = None

    @field_validator("allowed_operations", mode="before")
    @classmethod
    def coerce_allowed_operations(cls, value: Any) -> list[str] | None:
        if value is None:
            return None
        if isinstance(value, list):
            return [str(item) for item in value]
        return None


class ApiKeyBankScopeRow(BaseModel):
    """Bank scope row for a Hindsight scoped API key."""

    model_config = ConfigDict(extra="ignore")

    bank_id: str
    bank_internal_id: str | None = None


@dataclass(frozen=True)
class CallerPolicy:
    """Resolved caller policy shared by tenant and operation validator extensions."""

    org_id: str
    schema_name: str
    user_id: str | None
    api_key_id: str | None
    role: Literal["owner", "admin", "member"]
    allowed_bank_ids: frozenset[str] | None
    allowed_bank_internal_ids: frozenset[str] | None
    allowed_operations: frozenset[str] | None
    tenant_config: dict[str, Any] = field(default_factory=dict)

    @property
    def is_admin(self) -> bool:
        return self.role in {"owner", "admin"}


@dataclass(frozen=True)
class _CachedPolicy:
    policy: CallerPolicy
    expires_at_monotonic: float


class SupabasePolicyResolver:
    """Resolve Supabase JWTs and Hindsight scoped API keys into caller policies."""

    def __init__(self, config: dict[str, str]):
        self.supabase_url = (config.get("supabase_url") or "").rstrip("/")
        self.supabase_service_key = config.get("supabase_service_key")
        self.schema_prefix = config.get("schema_prefix", "org")
        self.cache_ttl_seconds = int(config.get("policy_cache_ttl_seconds", "5"))
        self._http_client: httpx.AsyncClient | None = None
        self._jwks_keys: dict[str, PyJWK] = {}
        self._jwks_last_fetched = 0.0
        self._use_jwks = False
        self._cache: dict[str, _CachedPolicy] = {}

        if not self.supabase_url:
            raise ValueError("HINDSIGHT_AUTH_SUPABASE_URL or HINDSIGHT_API_*_SUPABASE_URL is required")
        if not self.supabase_service_key:
            raise ValueError("HINDSIGHT_AUTH_SUPABASE_SERVICE_KEY or HINDSIGHT_API_*_SUPABASE_SERVICE_KEY is required")
        if not _SCHEMA_PREFIX_RE.match(self.schema_prefix):
            raise ValueError("schema_prefix must be a valid PostgreSQL identifier component")

    async def on_startup(self) -> None:
        await self._ensure_http_client()
        await self._try_init_jwks()

    async def on_shutdown(self) -> None:
        if self._http_client is not None:
            await self._http_client.aclose()
            self._http_client = None

    async def resolve(self, context: RequestContext) -> CallerPolicy:
        token = context.api_key
        if not token:
            raise AuthenticationError("Missing Authorization header. Expected: Bearer <supabase_jwt|hindsight_api_key>")
        if len(token) < MIN_TOKEN_LENGTH:
            raise AuthenticationError("Invalid credential format")

        cache_key = f"{token}:{context.selected_tenant_id or ''}"
        cached = self._cache.get(cache_key)
        now = time.monotonic()
        if cached and cached.expires_at_monotonic > now:
            return cached.policy

        if _JWT_SHAPE_RE.match(token):
            policy = await self._resolve_jwt(token, context.selected_tenant_id)
        else:
            policy = await self._resolve_api_key(token)

        self._cache[cache_key] = _CachedPolicy(policy=policy, expires_at_monotonic=now + self.cache_ttl_seconds)
        return policy

    async def list_tenants(self) -> list[Tenant]:
        rows = await self._rest_get("organizations", select="id")
        organizations = TypeAdapter(list[OrganizationRow]).validate_python(rows)
        return [Tenant(schema=self._schema_for_org(row.id), tenant_id=row.id) for row in organizations]

    async def _resolve_jwt(self, token: str, selected_tenant_id: str | None) -> CallerPolicy:
        if not selected_tenant_id:
            raise AuthenticationError("Missing X-Hindsight-Tenant-Id header for Supabase JWT requests")
        self._validate_org_id(selected_tenant_id)
        user_id = await self._verify_token(token)
        member = await self._get_member(selected_tenant_id, user_id)
        if member is None:
            raise AuthenticationError("User is not a member of the selected organization")
        organization = await self._get_organization(selected_tenant_id)
        if organization is None:
            raise AuthenticationError("Selected organization does not exist")
        return CallerPolicy(
            org_id=selected_tenant_id,
            schema_name=self._schema_for_org(selected_tenant_id),
            user_id=user_id,
            api_key_id=None,
            role=member.role,
            allowed_bank_ids=None,
            allowed_bank_internal_ids=None,
            allowed_operations=_operations_for_role(member.role),
            tenant_config=organization.config,
        )

    async def _resolve_api_key(self, api_key: str) -> CallerPolicy:
        key_hash = hashlib.sha256(api_key.encode("utf-8")).hexdigest()
        rows = await self._rest_get(
            "hindsight_api_keys",
            select="id,org_id,created_by_user_id,role,allowed_operations,bank_scope_mode,revoked_at,expires_at",
            key_hash=f"eq.{key_hash}",
            revoked_at="is.null",
            limit="1",
        )
        keys = TypeAdapter(list[ApiKeyRow]).validate_python(rows)
        if not keys:
            raise AuthenticationError("Invalid Hindsight API key")
        key = keys[0]
        if key.expires_at and _is_past_timestamp(key.expires_at):
            raise AuthenticationError("Hindsight API key has expired")
        creator_member = await self._get_member(key.org_id, key.created_by_user_id) if key.created_by_user_id else None
        if creator_member is None:
            raise AuthenticationError("API key creator is no longer a member of the organization")
        creator_operations = _operations_for_role(creator_member.role)
        key_operations = (
            frozenset(operation for operation in key.allowed_operations if operation in ALL_BANK_OPERATIONS)
            if key.allowed_operations is not None
            else creator_operations
        )
        effective_operations = key_operations & creator_operations
        allowed_bank_ids: frozenset[str] | None = None
        allowed_bank_internal_ids: frozenset[str] | None = None
        if key.bank_scope_mode == "selected":
            scope_rows = await self._rest_get(
                "hindsight_api_key_bank_scopes",
                select="bank_id,bank_internal_id",
                api_key_id=f"eq.{key.id}",
            )
            scopes = TypeAdapter(list[ApiKeyBankScopeRow]).validate_python(scope_rows)
            allowed_bank_ids = frozenset(scope.bank_id for scope in scopes)
            allowed_bank_internal_ids = frozenset(scope.bank_internal_id for scope in scopes if scope.bank_internal_id)
        organization = await self._get_organization(key.org_id)
        if organization is None:
            raise AuthenticationError("API key organization does not exist")
        return CallerPolicy(
            org_id=key.org_id,
            schema_name=self._schema_for_org(key.org_id),
            user_id=None,
            api_key_id=key.id,
            role=creator_member.role,
            allowed_bank_ids=allowed_bank_ids,
            allowed_bank_internal_ids=allowed_bank_internal_ids,
            allowed_operations=effective_operations,
            tenant_config=organization.config,
        )

    async def _get_member(self, org_id: str, user_id: str) -> MemberRow | None:
        rows = await self._rest_get(
            "organization_members",
            select="org_id,user_id,role",
            org_id=f"eq.{org_id}",
            user_id=f"eq.{user_id}",
            limit="1",
        )
        members = TypeAdapter(list[MemberRow]).validate_python(rows)
        return members[0] if members else None

    async def _get_organization(self, org_id: str) -> OrganizationRow | None:
        rows = await self._rest_get("organizations", select="id,name,config", id=f"eq.{org_id}", limit="1")
        organizations = TypeAdapter(list[OrganizationRow]).validate_python(rows)
        return organizations[0] if organizations else None

    async def _rest_get(self, table: str, **params: str) -> Any:
        await self._ensure_http_client()
        assert self._http_client is not None
        response = await self._http_client.get(
            f"{self.supabase_url}/rest/v1/{table}",
            params=params,
            headers={
                "apikey": self.supabase_service_key or "",
                "Authorization": f"Bearer {self.supabase_service_key}",
            },
        )
        if response.status_code >= 400:
            raise AuthenticationError(f"Supabase policy lookup failed: {response.status_code}")
        return response.json()

    async def _rest_post(self, table: str, body: dict[str, Any]) -> None:
        await self._ensure_http_client()
        assert self._http_client is not None
        response = await self._http_client.post(
            f"{self.supabase_url}/rest/v1/{table}",
            json=body,
            headers={
                "apikey": self.supabase_service_key or "",
                "Authorization": f"Bearer {self.supabase_service_key}",
                "Content-Type": "application/json",
            },
        )
        if response.status_code == 409:
            return
        if response.status_code >= 400:
            raise AuthenticationError(f"Supabase policy update failed: {response.status_code}")

    async def _try_init_jwks(self) -> None:
        try:
            await self._fetch_jwks()
            if self._jwks_keys:
                self._use_jwks = True
                return
        except Exception as exc:
            logger.warning("Could not fetch Supabase JWKS; falling back to /auth/v1/user: %s", exc)
        self._use_jwks = False

    async def _fetch_jwks(self) -> None:
        await self._ensure_http_client()
        assert self._http_client is not None
        response = await self._http_client.get(f"{self.supabase_url}/auth/v1/.well-known/jwks.json")
        response.raise_for_status()
        keys: dict[str, PyJWK] = {}
        for key_data in response.json().get("keys", []):
            kid = key_data.get("kid")
            if kid:
                keys[kid] = PyJWK(key_data)
        self._jwks_keys = keys
        self._jwks_last_fetched = time.monotonic()

    async def _verify_token(self, token: str) -> str:
        return await self._verify_token_jwks(token) if self._use_jwks else await self._verify_token_legacy(token)

    async def _verify_token_jwks(self, token: str) -> str:
        try:
            signing_key = await self._get_signing_key(token)
            payload = pyjwt.decode(
                token,
                signing_key.key,
                algorithms=SUPPORTED_ALGORITHMS,
                audience="authenticated",
                issuer=f"{self.supabase_url}/auth/v1",
            )
        except pyjwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except pyjwt.InvalidTokenError as exc:
            raise AuthenticationError(f"Invalid token: {exc!s}")
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError("Token valid but missing subject (sub) claim")
        return str(user_id)

    async def _get_signing_key(self, token: str) -> PyJWK:
        header = pyjwt.get_unverified_header(token)
        kid = header.get("kid")
        if not kid:
            raise AuthenticationError("Token missing key ID (kid) header")
        now = time.monotonic()
        if now - self._jwks_last_fetched > JWKS_CACHE_TTL_SECONDS:
            await self._fetch_jwks()
        if kid in self._jwks_keys:
            return self._jwks_keys[kid]
        if now - self._jwks_last_fetched > JWKS_MIN_REFRESH_INTERVAL_SECONDS:
            await self._fetch_jwks()
            if kid in self._jwks_keys:
                return self._jwks_keys[kid]
        raise AuthenticationError("Unable to find signing key for token")

    async def _verify_token_legacy(self, token: str) -> str:
        await self._ensure_http_client()
        assert self._http_client is not None
        response = await self._http_client.get(
            f"{self.supabase_url}/auth/v1/user",
            headers={"Authorization": f"Bearer {token}", "apikey": self.supabase_service_key or ""},
        )
        if response.status_code == 401:
            raise AuthenticationError("Invalid or expired token")
        if response.status_code != 200:
            raise AuthenticationError(f"Authentication failed: {response.status_code}")
        user_id = response.json().get("id")
        if not user_id:
            raise AuthenticationError("Token valid but no user ID found")
        return str(user_id)

    async def _ensure_http_client(self) -> None:
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS)

    def _schema_for_org(self, org_id: str) -> str:
        self._validate_org_id(org_id)
        return f"{self.schema_prefix}_{org_id.replace('-', '_')}"

    @staticmethod
    def _validate_org_id(org_id: str) -> None:
        if not _UUID_OR_SLUG_RE.match(org_id):
            raise AuthenticationError("Invalid organization ID")


def _resolver_config(config: dict[str, str]) -> dict[str, str]:
    """Accept both grouped auth env names and current extension-prefixed env names."""

    import os

    resolved = dict(config)
    if "supabase_url" not in resolved and os.getenv("HINDSIGHT_AUTH_SUPABASE_URL"):
        resolved["supabase_url"] = os.environ["HINDSIGHT_AUTH_SUPABASE_URL"]
    if "supabase_service_key" not in resolved and os.getenv("HINDSIGHT_AUTH_SUPABASE_SERVICE_KEY"):
        resolved["supabase_service_key"] = os.environ["HINDSIGHT_AUTH_SUPABASE_SERVICE_KEY"]
    if "schema_prefix" not in resolved and os.getenv("HINDSIGHT_AUTH_SCHEMA_PREFIX"):
        resolved["schema_prefix"] = os.environ["HINDSIGHT_AUTH_SCHEMA_PREFIX"]
    return resolved


def _is_past_timestamp(value: str) -> bool:
    normalized = value.replace("Z", "+00:00")
    try:
        expires_at = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise AuthenticationError("Hindsight API key has invalid expiration timestamp") from exc
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    return expires_at <= datetime.now(UTC)


def _operations_for_role(role: Literal["owner", "admin", "member"]) -> frozenset[str]:
    if role == "member":
        return MEMBER_BANK_OPERATIONS
    return ALL_BANK_OPERATIONS


class SupabaseOrgTenantExtension(TenantExtension):
    """Tenant extension that maps Supabase users or Hindsight API keys to organization schemas."""

    auth_profile = "supabase_org"
    auth_profile_component = "tenant"
    required_auth_profile_components = frozenset({"tenant", "operation_validator"})

    def __init__(self, config: dict[str, str]):
        super().__init__(config)
        self.resolver = SupabasePolicyResolver(_resolver_config(config))
        self._initialized_schemas: set[str] = set()
        self._schema_locks: dict[str, asyncio.Lock] = {}

    async def on_startup(self) -> None:
        await self.resolver.on_startup()

    async def on_shutdown(self) -> None:
        await self.resolver.on_shutdown()

    async def authenticate(self, context: RequestContext) -> TenantContext:
        policy = await self.resolver.resolve(context)
        await self._ensure_schema_ready(policy.schema_name)
        context.tenant_id = policy.org_id
        context.selected_tenant_id = policy.org_id
        context.subject_id = policy.user_id or policy.api_key_id
        context.subject_type = "user" if policy.user_id is not None else "api_key"
        context.api_key_id = policy.api_key_id
        context.role = policy.role
        context.allowed_bank_ids = sorted(policy.allowed_bank_ids) if policy.allowed_bank_ids is not None else None
        context.allowed_operations = (
            sorted(policy.allowed_operations) if policy.allowed_operations is not None else None
        )
        context.auth_policy = policy
        return TenantContext(schema_name=policy.schema_name)

    async def list_tenants(self) -> list[Tenant]:
        tenants = await self.resolver.list_tenants()
        self._initialized_schemas.update(tenant.schema for tenant in tenants)
        return tenants

    async def _ensure_schema_ready(self, schema_name: str) -> None:
        if schema_name in self._initialized_schemas:
            return
        lock = self._schema_locks.setdefault(schema_name, asyncio.Lock())
        async with lock:
            if schema_name in self._initialized_schemas:
                return
            logger.info("Initializing organization schema: %s", schema_name)
            try:
                await self.context.run_migration(schema_name)
            except Exception as exc:
                logger.error("Organization schema initialization failed for %s: %s", schema_name, exc)
                raise AuthenticationError(f"Failed to initialize organization schema: {exc!s}") from exc
            self._initialized_schemas.add(schema_name)
            logger.info("Organization schema ready: %s", schema_name)

    async def get_tenant_config(self, context: RequestContext) -> dict[str, Any]:
        policy = await self.resolver.resolve(context)
        return policy.tenant_config


class SupabaseAuthorizationExtension(OperationValidatorExtension):
    """Operation validator enforcing Cloud-like organization roles and operation-scoped API keys."""

    auth_profile = "supabase_org"
    auth_profile_component = "operation_validator"
    required_auth_profile_components = frozenset({"tenant", "operation_validator"})

    def __init__(self, config: dict[str, str]):
        super().__init__(config)
        self.resolver = SupabasePolicyResolver(_resolver_config(config))

    async def on_startup(self) -> None:
        await self.resolver.on_startup()

    async def on_shutdown(self) -> None:
        await self.resolver.on_shutdown()

    async def validate_retain(self, ctx: RetainContext) -> ValidationResult:
        return await self._validate_bank_operation(ctx.request_context, ctx.bank_id, "retain", write=True)

    async def validate_recall(self, ctx: RecallContext) -> ValidationResult:
        return await self._validate_bank_operation(ctx.request_context, ctx.bank_id, "recall", write=False)

    async def validate_reflect(self, ctx: ReflectContext) -> ValidationResult:
        return await self._validate_bank_operation(ctx.request_context, ctx.bank_id, "reflect", write=False)

    async def validate_bank_read(self, ctx: BankReadContext) -> ValidationResult:
        return await self._validate_bank_operation(ctx.request_context, ctx.bank_id, ctx.operation, write=False)

    async def validate_bank_write(self, ctx: BankWriteContext) -> ValidationResult:
        return await self._validate_bank_operation(ctx.request_context, ctx.bank_id, ctx.operation, write=True)

    async def filter_bank_list(self, ctx: BankListContext) -> BankListResult:
        policy = await self._resolve_policy(ctx.request_context)
        if policy.allowed_bank_ids is None:
            return BankListResult(banks=ctx.banks)
        allowed_internal_ids = policy.allowed_bank_internal_ids or frozenset()
        filtered = [bank for bank in ctx.banks if str(bank.get("internal_id") or "") in allowed_internal_ids]
        return BankListResult(banks=filtered)

    async def filter_mcp_tools(
        self,
        bank_id: str,
        request_context: RequestContext,
        tools: frozenset[str],
    ) -> frozenset[str]:
        policy = await self._resolve_policy(request_context)
        if not await self._can_access_bank_for_operation(policy, bank_id, "get_bank_profile", request_context):
            return frozenset()
        if policy.allowed_operations is None:
            return tools
        return frozenset(tool for tool in tools if self._tool_allowed(tool, policy.allowed_operations))

    async def _validate_bank_operation(
        self,
        request_context: RequestContext,
        bank_id: str,
        operation: str,
        *,
        write: bool,
    ) -> ValidationResult:
        policy = await self._resolve_policy(request_context)
        allowed_operations = policy.allowed_operations or _operations_for_role(policy.role)
        if operation not in allowed_operations:
            return ValidationResult.reject("Caller is not allowed to perform this operation", status_code=403)
        if not await self._can_access_bank_for_operation(policy, bank_id, operation, request_context):
            return ValidationResult.reject("Caller is not allowed to access this bank", status_code=403)
        return ValidationResult.accept()

    async def _resolve_policy(self, request_context: RequestContext) -> CallerPolicy:
        cached = request_context.auth_policy
        if isinstance(cached, CallerPolicy):
            return cached
        policy = await self.resolver.resolve(request_context)
        request_context.auth_policy = policy
        return policy

    async def _can_access_bank_for_operation(
        self,
        policy: CallerPolicy,
        bank_id: str,
        operation: str,
        request_context: RequestContext,
    ) -> bool:
        if policy.allowed_bank_ids is None:
            return True
        current_internal_id = await self._get_bank_internal_id(bank_id)
        if current_internal_id and current_internal_id in (policy.allowed_bank_internal_ids or frozenset()):
            return True
        if policy.api_key_id is None or operation != "retain":
            return False
        if current_internal_id:
            return False
        current_internal_id = await self._ensure_bank_exists_and_get_internal_id(bank_id, request_context)
        if not current_internal_id:
            return False
        await self.resolver._rest_post(
            "hindsight_api_key_bank_scopes",
            {
                "api_key_id": policy.api_key_id,
                "bank_id": bank_id,
                "bank_internal_id": current_internal_id,
            },
        )
        return True

    async def _get_bank_internal_id(self, bank_id: str) -> str | None:
        from hindsight_api.engine.retain import bank_utils

        memory = self.context.get_memory_engine()
        get_backend = getattr(memory, "_get_backend", None)
        if get_backend is None:
            return None
        backend = await get_backend()
        return await bank_utils.get_bank_internal_id_if_exists(backend, bank_id)

    async def _ensure_bank_exists_and_get_internal_id(
        self,
        bank_id: str,
        request_context: RequestContext,
    ) -> str | None:
        memory = self.context.get_memory_engine()
        ensure_bank_exists = getattr(memory, "_ensure_bank_exists", None)
        if ensure_bank_exists is not None:
            await ensure_bank_exists(bank_id, request_context)
        return await self._get_bank_internal_id(bank_id)

    @staticmethod
    def _tool_allowed(tool_name: str, allowed_operations: frozenset[str]) -> bool:
        if tool_name.startswith("retain"):
            return "retain" in allowed_operations
        if tool_name == "delete_bank":
            return "delete_bank" in allowed_operations
        if tool_name == "create_bank":
            return "update_bank" in allowed_operations
        if tool_name.startswith("reflect"):
            return "reflect" in allowed_operations
        if tool_name.startswith("recall") or tool_name in {"list_banks", "get_bank"}:
            return "recall" in allowed_operations or "get_bank_profile" in allowed_operations
        return True
