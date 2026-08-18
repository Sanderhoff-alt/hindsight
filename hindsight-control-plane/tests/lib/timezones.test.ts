import { describe, expect, it } from "vitest";

import {
  filterTimezoneOptions,
  getTimezoneOffset,
  mergeTimezoneChoices,
  type TimezoneOption,
} from "@/lib/timezones";

const options: TimezoneOption[] = [
  { timezone: "UTC", offset: "UTC+0" },
  { timezone: "Asia/Shanghai", offset: "UTC+8" },
  { timezone: "America/New_York", offset: "UTC-5" },
];

describe("mergeTimezoneChoices", () => {
  it("pins UTC first and keeps a non-browser current value selectable", () => {
    expect(
      mergeTimezoneChoices(["Asia/Shanghai", "America/New_York"], "Asia/Shanghai", "Etc/GMT-8")
    ).toEqual(["UTC", "Etc/GMT-8", "Asia/Shanghai", "America/New_York"]);
  });

  it("does not duplicate UTC, the browser timezone, or the current value", () => {
    expect(mergeTimezoneChoices(["UTC", "Asia/Shanghai"], "Asia/Shanghai", "UTC")).toEqual([
      "UTC",
      "Asia/Shanghai",
    ]);
  });
});

describe("filterTimezoneOptions", () => {
  it("filters by timezone name without matching every UTC offset", () => {
    expect(filterTimezoneOptions(options, "UTC").map((option) => option.timezone)).toEqual(["UTC"]);
    expect(filterTimezoneOptions(options, "asia").map((option) => option.timezone)).toEqual([
      "Asia/Shanghai",
    ]);
  });

  it("restores UTC as the first item when search is cleared", () => {
    expect(filterTimezoneOptions(options, "As")[0]?.timezone).toBe("Asia/Shanghai");
    expect(filterTimezoneOptions(options, "")[0]?.timezone).toBe("UTC");
  });
});

describe("getTimezoneOffset", () => {
  it("formats fixed UTC offsets for display", () => {
    expect(getTimezoneOffset("UTC", new Date("2026-01-01T00:00:00Z"))).toBe("UTC+0");
    expect(getTimezoneOffset("Asia/Shanghai", new Date("2026-01-01T00:00:00Z"))).toBe("UTC+8");
  });
});
