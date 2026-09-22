/**
 * Helpers for building URLs that include a bank id.
 *
 * Bank ids are user-defined and may contain characters that are not URL-safe
 * (e.g. openclaw composite ids like `agent-1::channel-2::user-3`, which contain
 * `:` and may also contain `%`, spaces, etc.). They must be percent-encoded
 * before being interpolated into a URL path or query string — both for client
 * navigation (`/banks/...`) and for calls to the control-plane proxy
 * (`/api/banks/...`).
 *
 * Always use these helpers instead of raw template literals.
 */

const enc = (value: string): string => encodeURIComponent(value);

/** Page route for a bank in the control plane app router. */
export function bankRoute(bankId: string, suffix = ""): string {
  return `/banks/${enc(bankId)}${suffix}`;
}

/** Control-plane proxy URL under `/api/banks/...` for a bank-scoped endpoint. */
export function bankApi(bankId: string, suffix = ""): string {
  return `/api/banks/${enc(bankId)}${suffix}`;
}

/** Control-plane proxy URL under `/api/stats/...` for bank statistics. */
export function bankStatsApi(bankId: string, suffix = ""): string {
  return `/api/stats/${enc(bankId)}${suffix}`;
}

/** Control-plane proxy URL for memory operations scoped to a bank via query string. */
export function memoryApi(memoryId: string, bankId: string, suffix = ""): string {
  return `/api/memories/${enc(memoryId)}${suffix}${suffix.includes("?") ? "&" : "?"}bank_id=${enc(bankId)}`;
}

/**
 * Control-plane proxy URL for document operations scoped to a bank via query parameters.
 *
 * Architectural Decision (Issue #4586, #4587):
 * Document IDs frequently contain forward slashes (e.g., file paths like `folder/doc.pdf` or S3 keys).
 * Previously, this endpoint was defined as a dynamic path route (`/api/documents/[documentId]`).
 * In cloud environments with HTTP reverse proxies (such as Envoy in Azure Container Apps or AWS ALB),
 * proxies normalize URI paths per RFC 3986 by decoding `%2F` into literal `/` before routing upstream.
 * In Next.js App Router, `[documentId]` strictly matches a single path segment; decoded slashes
 * split the ID across multiple segments, causing 404 route matching failures.
 *
 * Routing `document_id` via URL query parameters (`/api/documents?bank_id=...&document_id=...`)
 * guarantees immunity to reverse proxy path normalization, as query parameters are never parsed
 * as path segment delimiters.
 *
 * DO NOT refactor this back to dynamic path segments (`/api/documents/[documentId]`).
 */
export function documentApi(documentId: string, bankId: string): string {
  const params = new URLSearchParams({ bank_id: bankId, document_id: documentId });
  return `/api/documents?${params.toString()}`;
}

/**
 * Control-plane proxy URL for listing document chunks via query parameters.
 *
 * Uses static route `/api/documents/chunks` with query parameters to prevent
 * RFC 3986 path normalization issues when document IDs contain slashes.
 *
 * DO NOT refactor this back to dynamic path segments (`/api/documents/[documentId]/chunks`).
 */
export function documentChunksApi(
  documentId: string,
  bankId: string,
  options?: { limit?: number; offset?: number }
): string {
  const params = new URLSearchParams({ bank_id: bankId, document_id: documentId });
  if (options?.limit !== undefined) params.set("limit", options.limit.toString());
  if (options?.offset !== undefined) params.set("offset", options.offset.toString());
  return `/api/documents/chunks?${params.toString()}`;
}

/**
 * Control-plane proxy URL for reprocessing a document via query parameters.
 *
 * Uses static route `/api/documents/reprocess` with query parameters to prevent
 * RFC 3986 path normalization issues when document IDs contain slashes.
 *
 * DO NOT refactor this back to dynamic path segments (`/api/documents/[documentId]/reprocess`).
 */
export function documentReprocessApi(documentId: string, bankId: string): string {
  const params = new URLSearchParams({ bank_id: bankId, document_id: documentId });
  return `/api/documents/reprocess?${params.toString()}`;
}

/**
 * Control-plane proxy URL under `/api/chunks` for a specific chunk lookup.
 *
 * In the Dataplane (FastAPI), chunk IDs are built from `(bank_id, document_id, chunk_index)`
 * without escaping slashes. When document IDs contain slashes, the resulting chunk ID also
 * contains slashes (e.g. `bank_folder/doc.md_0`).
 *
 * Passing `chunk_id` via query parameter `/api/chunks?chunk_id=...` ensures that reverse proxies
 * do not decode slashes in chunk IDs into path separators that break route resolution.
 *
 * DO NOT refactor this back to dynamic path segments (`/api/chunks/[chunkId]`).
 */
export function chunkApi(chunkId: string): string {
  const params = new URLSearchParams({ chunk_id: chunkId });
  return `/api/chunks?${params.toString()}`;
}
