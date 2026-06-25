import { NextResponse } from "next/server";
import { localizeApiErrorPayload } from "@/lib/i18n/api-errors";
import { sdk, createDataplaneClientForRequest } from "@/lib/hindsight-client";
import { getControlPlaneAuthProvider } from "@/lib/auth/provider";
import { respondWithSdk } from "@/lib/sdk-response";
import { deleteApiKeyBankScopesByInternalId } from "@/lib/supabase-org/store";

interface BankListItem {
  bank_id: string;
  internal_id?: string | null;
}

export async function PUT(request: Request, { params }: { params: Promise<{ bankId: string }> }) {
  const { bankId } = await params;
  let body;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json(
      localizeApiErrorPayload(request, {
        error: "Invalid JSON body",
        errorKey: "api.errors.auth.invalidRequestBody",
      }),
      { status: 400 }
    );
  }

  if (!bankId) {
    return NextResponse.json(
      localizeApiErrorPayload(request, {
        error: "bank_id is required",
        errorKey: "api.errors.validation.bankIdRequired",
      }),
      { status: 400 }
    );
  }

  const response = await sdk.createOrUpdateBank({
    client: createDataplaneClientForRequest(request),
    path: { bank_id: bankId },
    body: {
      name: body.name,
      mission: body.mission,
      disposition: body.disposition,
    },
  });
  return respondWithSdk(response, "Failed to update bank", { request });
}

export async function PATCH(request: Request, { params }: { params: Promise<{ bankId: string }> }) {
  const { bankId } = await params;
  let body;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json(
      localizeApiErrorPayload(request, {
        error: "Invalid JSON body",
        errorKey: "api.errors.auth.invalidRequestBody",
      }),
      { status: 400 }
    );
  }

  if (!bankId) {
    return NextResponse.json(
      localizeApiErrorPayload(request, {
        error: "bank_id is required",
        errorKey: "api.errors.validation.bankIdRequired",
      }),
      { status: 400 }
    );
  }

  const response = await sdk.updateBank({
    client: createDataplaneClientForRequest(request),
    path: { bank_id: bankId },
    body: {
      name: body.name,
      mission: body.mission,
      disposition: body.disposition,
    },
  });
  return respondWithSdk(response, "Failed to update bank", { request });
}

export async function DELETE(
  request: Request,
  { params }: { params: Promise<{ bankId: string }> }
) {
  const { bankId } = await params;

  if (!bankId) {
    return NextResponse.json(
      localizeApiErrorPayload(request, {
        error: "bank_id is required",
        errorKey: "api.errors.validation.bankIdRequired",
      }),
      { status: 400 }
    );
  }

  const shouldCleanupApiKeyScopes = getControlPlaneAuthProvider() === "supabase_org";
  const bankInternalId = shouldCleanupApiKeyScopes
    ? await resolveBankInternalId(request, bankId)
    : null;
  const response = await sdk.deleteBank({
    client: createDataplaneClientForRequest(request),
    path: { bank_id: bankId },
  });
  if (response.error === undefined && response.data !== undefined && bankInternalId) {
    await cleanupDeletedBankApiKeyScopes(bankInternalId);
  }
  return respondWithSdk(response, "Failed to delete bank", { request });
}

async function cleanupDeletedBankApiKeyScopes(bankInternalId: string): Promise<void> {
  try {
    await deleteApiKeyBankScopesByInternalId(bankInternalId);
  } catch (error) {
    console.warn("Failed to clean deleted bank API key scopes", {
      bankInternalId,
      error,
    });
  }
}

async function resolveBankInternalId(request: Request, bankId: string): Promise<string | null> {
  const response = await sdk.listBanks({ client: createDataplaneClientForRequest(request) });
  if (response.error || !response.data) return null;
  const banks = (response.data as { banks?: BankListItem[] }).banks ?? [];
  return banks.find((bank) => bank.bank_id === bankId)?.internal_id ?? null;
}
