import { NextResponse } from "next/server";

import {
  type ApiKeyBankScopeInput,
  type ApiKeyOperation,
  type ApiKeyOperationScopeInput,
  type ApiKeyPermissionMode,
  type HindsightApiKeySummary,
  createApiKey,
  getCurrentOrgContext,
  jsonError,
  listApiKeys,
  repairApiKeyBankReferences,
} from "@/lib/supabase-org/store";
import { createDataplaneClientForRequest, sdk } from "@/lib/hindsight-client";

interface BankListItem {
  bank_id: string;
  internal_id?: string | null;
  name?: string | null;
}

export async function GET(request: Request) {
  try {
    const context = await getCurrentOrgContext(request);
    const apiKeys = await listApiKeys(context);
    const currentBanks = await listCurrentBanks(request);
    const currentBankIdByInternalId = new Map(
      currentBanks
        .filter((bank): bank is BankListItem & { internal_id: string } => Boolean(bank.internal_id))
        .map((bank) => [bank.internal_id, bank.bank_id])
    );
    const currentBankByInternalId = new Map(
      currentBanks
        .filter((bank): bank is BankListItem & { internal_id: string } => Boolean(bank.internal_id))
        .map((bank) => [bank.internal_id, bank])
    );
    try {
      await repairApiKeyBankReferences(apiKeys, Array.from(currentBankByInternalId.keys()));
    } catch (error) {
      // Read repair is best-effort: stale references are already filtered from the response,
      // so a Supabase cleanup failure must not make API key management unavailable.
      console.warn("Failed to repair stale API key bank references", { error });
    }
    return NextResponse.json(
      {
        api_keys: apiKeys.map((apiKey) => {
          const ownedBanks = (apiKey.owned_banks ?? [])
            .map((ownedBank) => {
              const currentBank = currentBankByInternalId.get(ownedBank.bank_internal_id);
              if (!currentBank) return null;
              return {
                ...ownedBank,
                bank_id: currentBank.bank_id,
                name: currentBank.name ?? ownedBank.name ?? null,
              };
            })
            .filter((bank): bank is NonNullable<typeof bank> => Boolean(bank));
          const publicApiKey = { ...toPublicApiKeySummary(apiKey), owned_banks: ownedBanks };
          return {
            ...publicApiKey,
            operation_scopes: (apiKey.operation_scopes ?? []).map((scope) => {
              const { scoped_bank_internal_ids: internalIds, ...publicScope } = scope;
              return {
                ...publicScope,
                scoped_bank_ids:
                  scope.bank_scope_mode === "selected"
                    ? (internalIds ?? [])
                        .map((internalId) => currentBankIdByInternalId.get(internalId))
                        .filter((bankId): bankId is string => Boolean(bankId))
                    : undefined,
              };
            }),
          };
        }),
      },
      { status: 200 }
    );
  } catch (error) {
    return jsonError(error instanceof Error ? error.message : "Failed to list API keys", 400);
  }
}

export async function POST(request: Request) {
  try {
    const body = (await request.json()) as {
      name?: string;
      permission_mode?: ApiKeyPermissionMode;
      operation_scopes?: Array<{
        operation?: string;
        bank_scope_mode?: "all" | "selected";
        bank_ids?: string[] | null;
      }> | null;
    };
    if (!body.name) return jsonError("name is required", 400);
    const permissionMode = body.permission_mode ?? "scoped";
    if (permissionMode !== "scoped" && permissionMode !== "full_access") {
      return jsonError("Invalid API key permission mode", 400);
    }
    const context = await getCurrentOrgContext(request);
    const operationScopes =
      permissionMode === "scoped"
        ? await resolveOperationScopes(request, body.operation_scopes ?? null)
        : null;
    const apiKey = await createApiKey(context, body.name, permissionMode, operationScopes);
    return NextResponse.json({ api_key: apiKey }, { status: 201 });
  } catch (error) {
    return jsonError(error instanceof Error ? error.message : "Failed to create API key", 400);
  }
}

export async function resolveOperationScopes(
  request: Request,
  scopes: Array<{
    operation?: string;
    bank_scope_mode?: "all" | "selected";
    bank_ids?: string[] | null;
  }> | null
): Promise<ApiKeyOperationScopeInput[] | null> {
  if (!scopes) return null;
  return Promise.all(
    scopes.map(async (scope) => {
      if (!scope.operation) throw new Error("operation is required");
      const bankScopeMode = scope.bank_scope_mode ?? "all";
      return {
        operation: scope.operation as ApiKeyOperation,
        bank_scope_mode: bankScopeMode,
        bank_scopes:
          bankScopeMode === "selected"
            ? await resolveBankScopes(request, scope.bank_ids ?? [])
            : [],
      };
    })
  );
}

async function resolveBankScopes(
  request: Request,
  bankIds: string[]
): Promise<ApiKeyBankScopeInput[]> {
  const uniqueBankIds = Array.from(new Set(bankIds.map((bankId) => bankId.trim()).filter(Boolean)));
  if (uniqueBankIds.length === 0) return [];
  const banks = (await listCurrentBanks(request)).filter(
    (bank): bank is BankListItem & { internal_id: string } => Boolean(bank.internal_id)
  );
  const bankById = new Map(banks.map((bank) => [bank.bank_id, bank]));
  return uniqueBankIds.map((bankId) => {
    const bank = bankById.get(bankId);
    if (!bank) throw new Error(`Selected bank does not exist: ${bankId}`);
    return { bank_id: bank.bank_id, bank_internal_id: bank.internal_id };
  });
}

async function listCurrentBanks(request: Request): Promise<BankListItem[]> {
  const response = await sdk.listBanks({ client: createDataplaneClientForRequest(request) });
  if (response.error || !response.data) {
    throw new Error("Failed to resolve selected banks");
  }
  return (response.data as { banks?: BankListItem[] }).banks ?? [];
}

function toPublicApiKeySummary(apiKey: HindsightApiKeySummary): HindsightApiKeySummary {
  const publicApiKey = { ...apiKey };
  publicApiKey.operation_scopes = (publicApiKey.operation_scopes ?? []).map((scope) => {
    const publicScope = { ...scope };
    delete publicScope.scoped_bank_internal_ids;
    return publicScope;
  });
  return publicApiKey;
}
