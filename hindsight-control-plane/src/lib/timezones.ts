export function getBrowserTimezone(): string {
  if (typeof window === "undefined") return "UTC";
  return Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";
}

export interface TimezoneOption {
  timezone: string;
  offset: string;
}

const offsetFormatters = new Map<string, Intl.DateTimeFormat>();

export function mergeTimezoneChoices(
  supported: readonly string[],
  browserTimezone: string,
  currentValue: string
): string[] {
  const choices = ["UTC", ...supported.filter((timezone) => timezone !== "UTC")];

  for (const timezone of [browserTimezone, currentValue]) {
    if (timezone && !choices.includes(timezone)) choices.splice(1, 0, timezone);
  }
  return choices;
}

export function getTimezoneOffset(timezone: string, now: Date): string {
  try {
    let formatter = offsetFormatters.get(timezone);
    if (!formatter) {
      formatter = new Intl.DateTimeFormat("en-US", {
        timeZone: timezone,
        timeZoneName: "longOffset",
      });
      offsetFormatters.set(timezone, formatter);
    }

    const offset = formatter.formatToParts(now).find((part) => part.type === "timeZoneName")?.value;
    if (!offset || offset === "GMT") return "UTC+0";
    return offset
      .replace(/^GMT/, "UTC")
      .replace(/([+-])0(\d)/, "$1$2")
      .replace(/:00$/, "");
  } catch {
    return "";
  }
}

export function filterTimezoneOptions(
  options: readonly TimezoneOption[],
  search: string
): readonly TimezoneOption[] {
  const query = search.trim().toLocaleLowerCase();
  if (!query) return options;
  return options.filter((option) => option.timezone.toLocaleLowerCase().includes(query));
}
