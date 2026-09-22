import { describe, expect, it } from "vitest";
import {
  bankApi,
  bankRoute,
  bankStatsApi,
  chunkApi,
  documentApi,
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
      expect(bankRoute("team/alpha")).toBe("/banks/team%2Falpha");
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
      expect(bankStatsApi("team/alpha")).toBe("/api/stats/team%2Falpha");
    });
  });

  describe("memoryApi", () => {
    it("builds memory API route with bank_id query param", () => {
      expect(memoryApi("mem-1", "bank-1")).toBe("/api/memories/mem-1?bank_id=bank-1");
      expect(memoryApi("mem-1", "bank-1", "/history")).toBe(
        "/api/memories/mem-1/history?bank_id=bank-1"
      );
    });

    it("encodes slashes and special characters in both memoryId and bankId", () => {
      expect(memoryApi("mem/special#1", "team/alpha")).toBe(
        "/api/memories/mem%2Fspecial%231?bank_id=team%2Falpha"
      );
    });

    it("correctly appends bank_id when suffix already has query params", () => {
      expect(memoryApi("mem-1", "bank-1", "/history?limit=10")).toBe(
        "/api/memories/mem-1/history?limit=10&bank_id=bank-1"
      );
    });
  });

  describe("documentApi", () => {
    it("builds standard document API route with bank_id", () => {
      expect(documentApi("doc-1", "bank-1")).toBe("/api/documents/doc-1?bank_id=bank-1");
    });

    it("encodes document ID containing slashes", () => {
      expect(documentApi("folder/subfolder/file.md", "bank-1")).toBe(
        "/api/documents/folder%2Fsubfolder%2Ffile.md?bank_id=bank-1"
      );
    });

    it("encodes bank ID containing special characters", () => {
      expect(documentApi("doc-1", "agent::channel::user")).toBe(
        "/api/documents/doc-1?bank_id=agent%3A%3Achannel%3A%3Auser"
      );
    });

    it("supports suffix like /reprocess or /chunks", () => {
      expect(documentApi("folder/doc.md", "bank-1", "/reprocess")).toBe(
        "/api/documents/folder%2Fdoc.md/reprocess?bank_id=bank-1"
      );
      expect(documentApi("folder/doc.md", "bank-1", "/chunks")).toBe(
        "/api/documents/folder%2Fdoc.md/chunks?bank_id=bank-1"
      );
    });

    it("supports suffix containing query parameters", () => {
      expect(documentApi("folder/doc.md", "bank-1", "/chunks?limit=50")).toBe(
        "/api/documents/folder%2Fdoc.md/chunks?limit=50&bank_id=bank-1"
      );
    });
  });

  describe("chunkApi", () => {
    it("builds standard chunk API route", () => {
      expect(chunkApi("chunk-123")).toBe("/api/chunks/chunk-123");
    });

    it("encodes chunk ID containing slashes from document path", () => {
      expect(chunkApi("bank-1_folder/example_0")).toBe(
        "/api/chunks/bank-1_folder%2Fexample_0"
      );
    });

    it("encodes reserved characters in chunk ID", () => {
      expect(chunkApi("bank_id::special/doc#1_0")).toBe(
        "/api/chunks/bank_id%3A%3Aspecial%2Fdoc%231_0"
      );
    });
  });
});
