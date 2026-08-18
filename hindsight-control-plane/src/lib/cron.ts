import { CronExpressionParser } from "cron-parser";

/**
 * Next scheduled run for a cron expression in the trigger's timezone. Missing
 * timezones intentionally default to UTC for older trigger payloads.
 */
export function nextCronRun(
  cron: string | null | undefined,
  timezone?: string | null
): Date | null {
  const expr = cron?.trim();
  if (!expr) return null;
  try {
    return CronExpressionParser.parse(expr, { tz: timezone || "UTC" })
      .next()
      .toDate();
  } catch {
    return null;
  }
}
