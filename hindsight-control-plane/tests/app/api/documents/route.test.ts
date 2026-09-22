import type { NextRequest } from "next/server";
import { beforeEach, describe, expect, it, vi } from "vitest";

type ListDocumentsArg = { query: Record<string, unknown> };
type GetDocumentArg = { path: { bank_id: string; document_id: string } };
type DeleteDocumentArg = { path: { bank_id: string; document_id: string } };

const { listDocuments, getDocument, deleteDocument, dataplaneBankUrl, getDataplaneHeaders } =
  vi.hoisted(() => ({
    listDocuments: vi.fn<(arg: ListDocumentsArg) => Promise<unknown>>(),
    getDocument: vi.fn<(arg: GetDocumentArg) => Promise<unknown>>(),
    deleteDocument: vi.fn<(arg: DeleteDocumentArg) => Promise<unknown>>(),
    dataplaneBankUrl: vi.fn((bankId: string, suffix = "") => `http://dataplane/v1/default/banks/${bankId}${suffix}`),
    getDataplaneHeaders: vi.fn(() => ({ "Authorization": "Bearer test" })),
  }));

vi.mock("@/lib/hindsight-client", () => ({
  sdk: { listDocuments, getDocument, deleteDocument },
  lowLevelClient: {},
  dataplaneBankUrl,
  getDataplaneHeaders,
}));

vi.mock("@/lib/sdk-response", () => ({
  respondWithSdk: vi.fn((response: unknown) => new Response(JSON.stringify(response), { status: 200 })),
}));

import { DELETE, GET, PATCH } from "@/app/api/documents/route";

function makeRequest(url: string, options?: { method?: string; body?: unknown }): NextRequest {
  const req = {
    nextUrl: new URL(url),
    method: options?.method || "GET",
    json: async () => options?.body,
  } as unknown as NextRequest;
  return req;
}

describe("/api/documents route handlers", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    listDocuments.mockResolvedValue({ data: { items: [], total: 0 }, error: undefined });
    getDocument.mockResolvedValue({ data: { id: "doc-1", title: "Test" }, error: undefined });
    deleteDocument.mockResolvedValue({ data: { success: true }, error: undefined });
  });

  describe("GET /api/documents", () => {
    it("returns 400 when bank_id is missing", async () => {
      const res = await GET(makeRequest("http://localhost/api/documents"));
      expect(res.status).toBe(400);
      const data = await res.json();
      expect(data.error).toBe("bank_id is required");
    });

    it("fetches single document when document_id is provided, preserving slashes", async () => {
      await GET(
        makeRequest("http://localhost/api/documents?bank_id=b1&document_id=folder%2Fexample.md")
      );

      expect(getDocument).toHaveBeenCalledTimes(1);
      expect(getDocument).toHaveBeenCalledWith({
        client: {},
        path: { bank_id: "b1", document_id: "folder/example.md" },
      });
      expect(listDocuments).not.toHaveBeenCalled();
    });

    it("forwards the `q` search term to the dataplane (search by document ID)", async () => {
      await GET(makeRequest("http://localhost/api/documents?bank_id=b1&q=my-doc-id&limit=25&offset=0"));

      expect(listDocuments).toHaveBeenCalledTimes(1);
      expect(listDocuments.mock.calls[0][0].query).toMatchObject({ q: "my-doc-id" });
    });

    it("omits `q` when no search term is provided", async () => {
      await GET(makeRequest("http://localhost/api/documents?bank_id=b1&limit=25&offset=0"));

      expect(listDocuments.mock.calls[0][0].query.q).toBeUndefined();
    });

    it("forwards repeated `tags` params and `tags_match` to the dataplane", async () => {
      await GET(
        makeRequest("http://localhost/api/documents?bank_id=b1&tags=alpha&tags=beta&tags_match=all_strict")
      );

      expect(listDocuments.mock.calls[0][0].query).toMatchObject({
        tags: ["alpha", "beta"],
        tags_match: "all_strict",
      });
    });

    it("omits `tags` when none are provided", async () => {
      await GET(makeRequest("http://localhost/api/documents?bank_id=b1"));

      expect(listDocuments.mock.calls[0][0].query.tags).toBeUndefined();
    });

    it("drops `tags_match` when no tags are filtered, so the dataplane default stands", async () => {
      await GET(makeRequest("http://localhost/api/documents?bank_id=b1&tags_match=all_strict"));

      expect(listDocuments.mock.calls[0][0].query.tags_match).toBeUndefined();
    });

    it("rejects an unknown `tags_match` value rather than passing it through", async () => {
      await GET(makeRequest("http://localhost/api/documents?bank_id=b1&tags=alpha&tags_match=bogus"));

      expect(listDocuments.mock.calls[0][0].query).toMatchObject({ tags: ["alpha"] });
      expect(listDocuments.mock.calls[0][0].query.tags_match).toBeUndefined();
    });
  });

  describe("PATCH /api/documents", () => {
    it("returns 400 when bank_id is missing", async () => {
      const res = await PATCH(makeRequest("http://localhost/api/documents?document_id=doc1"));
      expect(res.status).toBe(400);
      const data = await res.json();
      expect(data.error).toBe("bank_id is required");
    });

    it("returns 400 when document_id is missing", async () => {
      const res = await PATCH(makeRequest("http://localhost/api/documents?bank_id=b1"));
      expect(res.status).toBe(400);
      const data = await res.json();
      expect(data.error).toBe("document_id is required");
    });

    it("forwards tags update to dataplane with encoded document ID", async () => {
      const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(
        new Response(JSON.stringify({ success: true }), { status: 200 })
      );

      const res = await PATCH(
        makeRequest("http://localhost/api/documents?bank_id=b1&document_id=folder%2Fexample.md", {
          body: { tags: ["t1", "t2"] },
        })
      );

      expect(res.status).toBe(200);
      expect(fetchSpy).toHaveBeenCalledWith(
        "http://dataplane/v1/default/banks/b1/documents/folder%2Fexample.md",
        expect.objectContaining({
          method: "PATCH",
          body: JSON.stringify({ tags: ["t1", "t2"] }),
        })
      );

      fetchSpy.mockRestore();
    });
  });

  describe("DELETE /api/documents", () => {
    it("returns 400 when bank_id is missing", async () => {
      const res = await DELETE(makeRequest("http://localhost/api/documents?document_id=doc1"));
      expect(res.status).toBe(400);
      const data = await res.json();
      expect(data.error).toBe("bank_id is required");
    });

    it("returns 400 when document_id is missing", async () => {
      const res = await DELETE(makeRequest("http://localhost/api/documents?bank_id=b1"));
      expect(res.status).toBe(400);
      const data = await res.json();
      expect(data.error).toBe("document_id is required");
    });

    it("deletes document with decoded document_id", async () => {
      await DELETE(
        makeRequest("http://localhost/api/documents?bank_id=b1&document_id=folder%2Fexample.md")
      );

      expect(deleteDocument).toHaveBeenCalledTimes(1);
      expect(deleteDocument).toHaveBeenCalledWith({
        client: {},
        path: { bank_id: "b1", document_id: "folder/example.md" },
      });
    });
  });
});
