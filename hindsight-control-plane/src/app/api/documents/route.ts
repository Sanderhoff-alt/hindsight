import { NextRequest, NextResponse } from "next/server";
import { localizeApiErrorPayload } from "@/lib/i18n/api-errors";
import { sdk, lowLevelClient, dataplaneBankUrl, getDataplaneHeaders } from "@/lib/hindsight-client";
import { respondWithSdk } from "@/lib/sdk-response";

// Tag matching modes accepted by the dataplane's list_documents endpoint.
const TAGS_MATCH_MODES = new Set(["any", "all", "any_strict", "all_strict", "exact"]);

// Time axes accepted by list_documents. Validated here rather than passed through so a
// typo is a dropped parameter, not a 422 from the dataplane.
type TimeField = "created_at" | "updated_at";
const TIME_FIELDS = new Set<string>(["created_at", "updated_at"]);

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const bankId = searchParams.get("bank_id");

  if (!bankId) {
    return NextResponse.json(
      localizeApiErrorPayload(request, {
        error: "bank_id is required",
        errorKey: "api.errors.validation.bankIdRequired",
      }),
      { status: 400 }
    );
  }

  // Architectural Decision (Issue #4586):
  // Single document retrieval is handled here via `?document_id=...` rather than
  // an independent dynamic route (`/api/documents/[documentId]`).
  // In cloud deployments with reverse proxies (e.g. Envoy on Azure Container Apps, AWS ALB),
  // proxies normalize URL paths per RFC 3986, decoding `%2F` into `/`. When document IDs
  // contain slashes (e.g. file paths or S3 keys), dynamic segment matching fails with 404
  // because the ID is split across multiple path segments. Query parameters are never
  // normalized or split into path segments by proxies.
  // DO NOT refactor this back into `/api/documents/[documentId]`.
  const documentId = searchParams.get("document_id");
  if (documentId) {
    const response = await sdk.getDocument({
      client: lowLevelClient,
      path: { bank_id: bankId, document_id: documentId },
    });
    return respondWithSdk(response, "Failed to fetch document", { request });
  }

  const q = searchParams.get("q") || undefined;
  const limit = searchParams.get("limit") ? Number(searchParams.get("limit")) : undefined;
  const offset = searchParams.get("offset") ? Number(searchParams.get("offset")) : undefined;
  const tagList = searchParams.getAll("tags").filter((tag) => tag.length > 0);
  const tags = tagList.length > 0 ? tagList : undefined;
  // Only forward tags_match alongside tags — on its own it would override the
  // dataplane default for an unfiltered listing.
  const tagsMatchParam = searchParams.get("tags_match");
  const tagsMatch =
    tags && tagsMatchParam && TAGS_MATCH_MODES.has(tagsMatchParam) ? tagsMatchParam : undefined;

  const timeFieldParam = searchParams.get("time_field");
  // Set.has() does not narrow, so the cast is what carries the check into the type.
  const timeField = TIME_FIELDS.has(timeFieldParam ?? "")
    ? (timeFieldParam as TimeField)
    : undefined;
  const startDate = searchParams.get("start_date") || undefined;
  const endDate = searchParams.get("end_date") || undefined;

  const response = await sdk.listDocuments({
    client: lowLevelClient,
    path: { bank_id: bankId },
    query: {
      q,
      tags,
      tags_match: tagsMatch,
      time_field: timeField,
      start_date: startDate,
      end_date: endDate,
      limit,
      offset,
    },
  });
  return respondWithSdk(response, "Failed to fetch documents", { request });
}

export async function PATCH(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const bankId = searchParams.get("bank_id");
    const documentId = searchParams.get("document_id");

    if (!bankId) {
      return NextResponse.json(
        localizeApiErrorPayload(request, {
          error: "bank_id is required",
          errorKey: "api.errors.validation.bankIdRequired",
        }),
        { status: 400 }
      );
    }

    if (!documentId) {
      return NextResponse.json(
        localizeApiErrorPayload(request, {
          error: "document_id is required",
          errorKey: "api.errors.validation.documentIdRequired",
        }),
        { status: 400 }
      );
    }

    const body = await request.json();
    const response = await fetch(
      dataplaneBankUrl(bankId, `/documents/${encodeURIComponent(documentId)}`),
      {
        method: "PATCH",
        headers: getDataplaneHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify(body),
      }
    );

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      return NextResponse.json(error, { status: response.status });
    }

    const data = await response.json();
    return NextResponse.json(data, { status: 200 });
  } catch (error) {
    console.error("Error updating document tags:", error);
    return NextResponse.json(
      localizeApiErrorPayload(request, {
        error: "Failed to update document tags",
        errorKey: "api.errors.documents.updateTags",
      }),
      { status: 500 }
    );
  }
}

export async function DELETE(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const bankId = searchParams.get("bank_id");
  const documentId = searchParams.get("document_id");

  if (!bankId) {
    return NextResponse.json(
      localizeApiErrorPayload(request, {
        error: "bank_id is required",
        errorKey: "api.errors.validation.bankIdRequired",
      }),
      { status: 400 }
    );
  }

  if (!documentId) {
    return NextResponse.json(
      localizeApiErrorPayload(request, {
        error: "document_id is required",
        errorKey: "api.errors.validation.documentIdRequired",
      }),
      { status: 400 }
    );
  }

  const response = await sdk.deleteDocument({
    client: lowLevelClient,
    path: { bank_id: bankId, document_id: documentId },
  });
  return respondWithSdk(response, "Failed to delete document", { request });
}
