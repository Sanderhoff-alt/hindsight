"use client";

import { useTranslations } from "next-intl";
import cronstrue from "cronstrue";
import { CronExpressionParser } from "cron-parser";
import { formatRelativeTime } from "@/lib/relative-time";
import { getBrowserTimezone, getTimezoneOffset } from "@/lib/timezones";

/**
 * Live preview for a cron expression in the trigger's timezone. Each run is also
 * shown in the viewer's local time when that differs from the schedule timezone.
 */
export function CronSchedulePreview({ cron, timezone }: { cron: string; timezone: string }) {
  const t = useTranslations("cronPreview");
  const expr = cron.trim();
  if (!expr) return null;
  const localTz = getBrowserTimezone();

  let human = "";
  const nextRuns: Date[] = [];
  try {
    human = cronstrue.toString(expr, { throwExceptionOnParseError: true });
    const it = CronExpressionParser.parse(expr, { tz: timezone });
    for (let i = 0; i < 3; i++) nextRuns.push(it.next().toDate());
  } catch {
    return (
      <div className="rounded-md border border-destructive/30 bg-destructive/5 px-3 py-2 text-xs text-destructive">
        {t("invalid")}
      </div>
    );
  }

  const fmtScheduled = (d: Date) =>
    d.toLocaleString("en-GB", {
      timeZone: timezone,
      day: "2-digit",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    });
  // Compare offsets rather than formatted strings: scheduled time uses a
  // fixed en-GB locale while local time uses the browser locale.
  const differsFromLocal = (d: Date) =>
    getTimezoneOffset(timezone, d) !== getTimezoneOffset(localTz, d);
  const fmtLocal = (d: Date) =>
    d.toLocaleString(undefined, {
      day: "2-digit",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    });
  const next = nextRuns[0];

  return (
    <div className="rounded-md border bg-muted/30 px-3 py-2.5 text-xs space-y-2">
      <div className="font-medium text-foreground">{human}</div>
      <div className="text-muted-foreground">
        {t("nextRun")}:{" "}
        <span className="text-foreground">{formatRelativeTime(next.toISOString())}</span>
        {" — "}
        {fmtScheduled(next)} {timezone}
      </div>
      <div className="text-muted-foreground">
        <div className="mb-0.5">{t("upcoming")}</div>
        <ul className="space-y-0.5">
          {nextRuns.map((d) => (
            <li key={d.toISOString()} className="font-mono">
              {fmtScheduled(d)} {timezone}
              {differsFromLocal(d) && (
                <span className="opacity-70">
                  {" · "}
                  {fmtLocal(d)} {t("local")}
                </span>
              )}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
