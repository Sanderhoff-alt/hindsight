import { describe, expect, it } from "vitest";
import {
  bankApi,
  bankRoute,
  bankStatsApi,
  chunkApi,
  documentApi,
  documentChunksApi,
  documentReprocessApi,
  memoryApi,
} from "@/lib/bank-url";

describe("bank-url helpers", () => {
  describe("bankRoute", () => {
    it("builds a standard bank route", () => {
      expect(bankRoute("bank-1")).toBe("/banks/bank-1");
      expect(bankRoute("bank-1", "/documents")).toBe("/banks/bank-1/documents");
    });

    it("encodes special characters in bank id", () => {
      expect(bankRoute("agent::channel::user")).toBe("/banks/agent%3A%3Achannel%3A%3Auser");
      expect(bankRoute("team-alpha")).toBe("/banks/team-alpha");
    });
  });

  describe("bankApi", () => {
    it("builds bank proxy API routes", () => {
      expect(bankApi("bank-1")).toBe("/api/banks/bank-1");
      expect(bankApi("bank-1", "/config")).toBe("/api/banks/bank-1/config");
    });

    it("encodes special characters in bank id", () => {
      expect(bankApi("agent::channel::user", "/config")).toBe(
        "/api/banks/agent%3A%3Achannel%3A%3Auser/config"
      );
    });
  });

  describe("bankStatsApi", () => {
    it("builds bank stats proxy API routes", () => {
      expect(bankStatsApi("bank-1")).toBe("/api/stats/bank-1");
      expect(bankStatsApi("team-alpha")).toBe("/api/stats/team-alpha");
    });
  });

  describe("memoryApi", () => {
    it("builds memory API route with bank_id query param", () => {
      expect(memoryApi("mem-1", "bank-1")).toBe("/api/memories/mem-1?bank_id=bank-1");
      expect(memoryApi("mem-1", "bank-1", "/history")).toBe(
        "/api/memories/mem-1/history?bank_id=bank-1"
      );
    });

    it("encodes special characters in memoryId and bankId", () => {
      expect(memoryApi("mem/special#1", "team-alpha")).toBe(
        "/api/memories/mem%2Fspecial%231?bank_id=team-alpha"
      );
    });

    it("correctly appends bank_id when suffix already has query params", () => {
      expect(memoryApi("mem-1", "bank-1", "/history?limit=10")).toBe(
        "/api/memories/mem-1/history?limit=10&bank_id=bank-1"
      );
    });
  });

  describe("documentApi", () => {
    it("builds document API route with query parameters", () => {
      expect(documentApi("doc-1", "bank-1")).toBe(
        "/api/documents?bank_id=bank-1&document_id=doc-1"
      );
    });

    it("handles document ID containing slashes", () => {
      expect(documentApi("folder/subfolder/file.md", "bank-1")).toBe(
        "/api/documents?bank_id=bank-1&document_id=folder%2Fsubfolder%2Ffile.md"
      );
    });

    it("encodes bank ID containing special characters", () => {
      expect(documentApi("doc-1", "agent::channel::user")).toBe(
        "/api/documents?bank_id=agent%3A%3Achannel%3A%3Auser&document_id=doc-1"
      );
    });
  });

  describe("documentChunksApi", () => {
    it("builds document chunks route with query parameters", () => {
      expect(documentChunksApi("folder/doc.md", "bank-1")).toBe(
        "/api/documents/chunks?bank_id=bank-1&document_id=folder%2Fdoc.md"
      );
    });

    it("includes pagination parameters when specified", () => {
      expect(documentChunksApi("folder/doc.md", "bank-1", { limit: 50, offset: 10 })).toBe(
        "/api/documents/chunks?bank_id=bank-1&document_id=folder%2Fdoc.md&limit=50&offset=10"
      );
    });
  });

  describe("documentReprocessApi", () => {
    it("builds document reprocess route with query parameters", () => {
      expect(documentReprocessApi("folder/doc.md", "bank-1")).toBe(
        "/api/documents/reprocess?bank_id=bank-1&document_id=folder%2Fdoc.md"
      );
    });
  });

  describe("chunkApi", () => {
    it("builds standard chunk API route using query parameters", () => {
      expect(chunkApi("chunk-123")).toBe("/api/chunks?chunk_id=chunk-123");
    });

    it("encodes chunk ID containing slashes from document path", () => {
      expect(chunkApi("bank-1_folder/example_0")).toBe(
        "/api/chunks?chunk_id=bank-1_folder%2Fexample_0"
      );
    });

    it("encodes reserved characters in chunk ID", () => {
      expect(chunkApi("bank_id::special/doc#1_0")).toBe(
        "/api/chunks?chunk_id=bank_id%3A%3Aspecial%2Fdoc%231_0"
      );
    });
  });
});
