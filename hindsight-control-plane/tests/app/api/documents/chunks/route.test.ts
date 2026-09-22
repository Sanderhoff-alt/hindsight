import type { NextRequest } from "next/server";
import { beforeEach, describe, expect, it, vi } from "vitest";

const { dataplaneBankUrl, getDataplaneHeaders } = vi.hoisted(() => ({
  dataplaneBankUrl: vi.fn((bankId: string, suffix = "") => `http://dataplane/v1/default/banks/${bankId}${suffix}`),
  getDataplaneHeaders: vi.fn(() => ({ Authorization: "Bearer test" })),
}));

vi.mock("@/lib/hindsight-client", () => ({
  dataplaneBankUrl,
  getDataplaneHeaders,
}));

import { GET } from "@/app/api/documents/chunks/route";

function makeRequest(url: string): NextRequest {
  return { nextUrl: new URL(url) } as unknown as NextRequest;
}

describe("GET /api/documents/chunks", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("returns 400 when bank_id is missing", async () => {
    const res = await GET(makeRequest("http://localhost/api/documents/chunks?document_id=doc1"));
    expect(res.status).toBe(400);
    const data = await res.json();
    expect(data.error).toBe("bank_id is required");
  });

  it("returns 400 when document_id is missing", async () => {
    const res = await GET(makeRequest("http://localhost/api/documents/chunks?bank_id=b1"));
    expect(res.status).toBe(400);
    const data = await res.json();
    expect(data.error).toBe("document_id is required");
  });

  it("forwards request to dataplane preserving slashes in document ID", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(
      new Response(JSON.stringify({ items: [], total: 0 }), { status: 200 })
    );

    const res = await GET(
      makeRequest("http://localhost/api/documents/chunks?bank_id=b1&document_id=folder%2Fexample.md&limit=50&offset=10")
    );

    expect(res.status).toBe(200);
    expect(dataplaneBankUrl).toHaveBeenCalledWith(
      "b1",
      "/documents/folder%2Fexample.md/chunks?limit=50&offset=10"
    );

    fetchSpy.mockRestore();
  });
});
