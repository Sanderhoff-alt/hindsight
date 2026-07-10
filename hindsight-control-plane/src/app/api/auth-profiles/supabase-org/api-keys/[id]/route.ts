import { NextResponse } from "next/server";

import {
  type ApiKeyBankScopeInput,
  type ApiKeyOperation,
  type ApiKeyOperationScopeInput,
  type ApiKeyPermissionMode,
  getCurrentOrgContext,
  jsonError,
  revealApiKey,
  revokeApiKey,
  updateApiKeyPermissions,
} from "@/lib/supabase-org/store";
import { createDataplaneClientForRequest, sdk } from "@/lib/hindsight-client";

interface BankListItem {
  bank_id: string;
  internal_id?: string | null;
}

export async function GET(request: Request, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params;
    const context = await getCurrentOrgContext(request);
    return NextResponse.json({ api_key: await revealApiKey(context, id) }, { status: 200 });
  } catch (error) {
    return jsonError(error instanceof Error ? error.message : "Failed to reveal API key", 400);
  }
}

async function resolveOperationScopes(
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

export async function DELETE(request: Request, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params;
    const context = await getCurrentOrgContext(request);
    await revokeApiKey(context, id);
    return NextResponse.json({ success: true }, { status: 200 });
  } catch (error) {
    return jsonError(error instanceof Error ? error.message : "Failed to revoke API key", 400);
  }
}

export async function PATCH(request: Request, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params;
    const body = (await request.json()) as {
      permission_mode?: ApiKeyPermissionMode;
      operation_scopes?: Array<{
        operation?: string;
        bank_scope_mode?: "all" | "selected";
        bank_ids?: string[] | null;
      }> | null;
    };
    const permissionMode = body.permission_mode ?? "scoped";
    if (permissionMode !== "scoped" && permissionMode !== "full_access") {
      return jsonError("Invalid API key permission mode", 400);
    }
    const context = await getCurrentOrgContext(request);
    const operationScopes =
      permissionMode === "scoped"
        ? await resolveOperationScopes(request, body.operation_scopes ?? null)
        : null;
    await updateApiKeyPermissions(context, id, permissionMode, operationScopes);
    return NextResponse.json({ success: true }, { status: 200 });
  } catch (error) {
    return jsonError(error instanceof Error ? error.message : "Failed to update API key", 400);
  }
}
