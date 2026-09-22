/**
 * Static route handler for document reprocessing.
 *
 * Architectural Decision (Issue #4586, #4587):
 * Document IDs frequently contain slashes (e.g. file paths like `folder/doc.pdf`).
 * Previously, this endpoint was defined under dynamic path `/api/documents/[documentId]/reprocess`.
 * In cloud deployments behind reverse proxies (such as Envoy in Azure Container Apps or AWS ALB),
 * reverse proxies normalize URI paths per RFC 3986 by decoding `%2F` into literal `/` before routing.
 * In Next.js App Router, dynamic segment `[documentId]` only matches a single path segment; decoded
 * slashes split the parameter across multiple segments, causing 404 route matching errors.
 *
 * By routing via a static path `/api/documents/reprocess` and reading `document_id` from URL query
 * parameters (`?bank_id=...&document_id=...`), this endpoint is immune to path normalization.
 *
 * DO NOT refactor this back to `/api/documents/[documentId]/reprocess`.
 */

import { NextRequest, NextResponse } from "next/server";
import { localizeApiErrorPayload } from "@/lib/i18n/api-errors";
import { dataplaneBankUrl, getDataplaneHeaders } from "@/lib/hindsight-client";

export async function POST(request: NextRequest) {
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

    const response = await fetch(
      dataplaneBankUrl(bankId, `/documents/${encodeURIComponent(documentId)}/reprocess`),
      {
        method: "POST",
        headers: getDataplaneHeaders({ "Content-Type": "application/json" }),
      }
    );

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      return NextResponse.json(error, { status: response.status });
    }

    const data = await response.json();
    return NextResponse.json(data, { status: 200 });
  } catch (error) {
    console.error("Error reprocessing document:", error);
    return NextResponse.json(
      localizeApiErrorPayload(request, {
        error: "Failed to reprocess document",
        errorKey: "api.errors.documents.reprocess",
      }),
      { status: 500 }
    );
  }
}
