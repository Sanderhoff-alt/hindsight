import { NextResponse } from "next/server";

import {
  type ApiKeyBankScopeInput,
  type HindsightApiKeySummary,
  createApiKey,
  getCurrentOrgContext,
  jsonError,
  listApiKeys,
} from "@/lib/supabase-org/store";
import { createDataplaneClientForRequest, sdk } from "@/lib/hindsight-client";

interface BankListItem {
  bank_id: string;
  internal_id?: string | null;
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
    return NextResponse.json(
      {
        api_keys: apiKeys.map((apiKey) => {
          const publicApiKey = toPublicApiKeySummary(apiKey);
          if (apiKey.bank_scope_mode !== "selected") return publicApiKey;
          const currentBankIds = (apiKey.scoped_bank_internal_ids ?? [])
            .map((internalId) => currentBankIdByInternalId.get(internalId))
            .filter((bankId): bankId is string => Boolean(bankId));
          return { ...publicApiKey, scoped_bank_ids: currentBankIds };
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
      bank_ids?: string[] | null;
      bank_scope_mode?: "all" | "selected";
      allowed_operations?: string[] | null;
    };
    if (!body.name) return jsonError("name is required", 400);
    const context = await getCurrentOrgContext(request);
    const bankScopes =
      body.bank_scope_mode === "selected"
        ? await resolveBankScopes(request, body.bank_ids ?? [])
        : null;
    const apiKey = await createApiKey(
      context,
      body.name,
      body.allowed_operations ?? null,
      body.bank_scope_mode ?? "all",
      bankScopes
    );
    return NextResponse.json({ api_key: apiKey }, { status: 201 });
  } catch (error) {
    return jsonError(error instanceof Error ? error.message : "Failed to create API key", 400);
  }
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

function toPublicApiKeySummary(
  apiKey: HindsightApiKeySummary
): Omit<HindsightApiKeySummary, "scoped_bank_internal_ids"> {
  const publicApiKey = { ...apiKey };
  delete publicApiKey.scoped_bank_internal_ids;
  return publicApiKey;
}
