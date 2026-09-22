import type { NextRequest } from "next/server";
import { beforeEach, describe, expect, it, vi } from "vitest";

type GetChunkArg = { path: { chunk_id: string } };

const { getChunk } = vi.hoisted(() => ({
  getChunk: vi.fn<(arg: GetChunkArg) => Promise<unknown>>(),
}));

vi.mock("@/lib/hindsight-client", () => ({
  sdk: { getChunk },
  lowLevelClient: {},
}));

vi.mock("@/lib/sdk-response", () => ({
  respondWithSdk: vi.fn((response: unknown) => new Response(JSON.stringify(response), { status: 200 })),
}));

import { GET } from "@/app/api/chunks/route";

function makeRequest(url: string): NextRequest {
  return { nextUrl: new URL(url) } as unknown as NextRequest;
}

describe("GET /api/chunks", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("returns 400 when chunk_id is missing", async () => {
    const res = await GET(makeRequest("http://localhost/api/chunks"));
    expect(res.status).toBe(400);
    const data = await res.json();
    expect(data.error).toBe("chunk_id is required");
  });

  it("forwards chunk_id with slashes to sdk.getChunk", async () => {
    getChunk.mockResolvedValueOnce({
      data: { chunk_id: "bank_folder/file.md_0", chunk_text: "sample" },
      error: undefined,
    });

    const res = await GET(
      makeRequest("http://localhost/api/chunks?chunk_id=bank_folder%2Ffile.md_0")
    );

    expect(res.status).toBe(200);
    expect(getChunk).toHaveBeenCalledWith({
      client: {},
      path: { chunk_id: "bank_folder/file.md_0" },
    });
  });
});
