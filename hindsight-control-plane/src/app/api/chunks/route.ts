/**
 * Static route handler for fetching chunk details.
 *
 * Architectural Decision (Issue #4586, #4587):
 * In the Dataplane (FastAPI), chunk IDs are built from `(bank_id, document_id, chunk_index)`
 * without escaping slashes. When document IDs contain slashes (e.g. file paths or S3 keys),
 * the generated chunk ID also contains slashes (e.g. `bank_folder/doc.md_0`).
 *
 * Previously, this endpoint was defined under dynamic path `/api/chunks/[chunkId]`.
 * In cloud deployments behind reverse proxies (such as Envoy in Azure Container Apps or AWS ALB),
 * reverse proxies normalize URI paths per RFC 3986 by decoding `%2F` into literal `/` before routing.
 * In Next.js App Router, dynamic segment `[chunkId]` only matches a single path segment; decoded
 * slashes split the parameter across multiple segments, causing 404 route matching errors.
 *
 * By routing via a static path `/api/chunks` and reading `chunk_id` from URL query
 * parameters (`?chunk_id=...`), this endpoint is immune to reverse proxy path normalization.
 *
 * DO NOT refactor this back to `/api/chunks/[chunkId]`.
 */

import { NextRequest, NextResponse } from "next/server";
import { sdk, lowLevelClient } from "@/lib/hindsight-client";
import { respondWithSdk } from "@/lib/sdk-response";
import { localizeApiErrorPayload } from "@/lib/i18n/api-errors";

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const chunkId = searchParams.get("chunk_id");

  if (!chunkId) {
    return NextResponse.json(
      localizeApiErrorPayload(request, {
        error: "chunk_id is required",
        errorKey: "api.errors.validation.chunkIdRequired",
      }),
      { status: 400 }
    );
  }

  const response = await sdk.getChunk({
    client: lowLevelClient,
    path: { chunk_id: chunkId },
  });
  return respondWithSdk(response, "Failed to fetch chunk", { request });
}
