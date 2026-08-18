"use client";

import { useTranslations } from "next-intl";
import { nextCronRun } from "@/lib/cron";
import { formatRelativeTime } from "@/lib/relative-time";

type TriggerLike = {
  refresh_after_consolidation?: boolean;
  refresh_cron?: string | null;
  timezone?: string | null;
};

/**
 * Inline "next refresh" value derived from a mental model's trigger:
 * - cron schedule -> relative time of the next run (absolute scheduled time on hover)
 * - after consolidation -> "after consolidation"
 * - otherwise (manual) -> "on demand"
 *
 * Renders only the value; call sites supply their own "Next refresh" label.
 */
export function NextRefresh({
  trigger,
  className,
}: {
  trigger?: TriggerLike | null;
  className?: string;
}) {
  const t = useTranslations("mentalModels");
  const cron = trigger?.refresh_cron?.trim();

  if (cron) {
    const timezone = trigger?.timezone || "UTC";
    const next = nextCronRun(cron, timezone);
    if (!next) return <span className={className}>{t("nextRefreshInvalid")}</span>;
    const scheduledTime = next.toLocaleString("en-GB", {
      timeZone: timezone,
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    });
    return (
      <span className={className} title={`${scheduledTime} ${timezone}`}>
        {formatRelativeTime(next.toISOString())}
      </span>
    );
  }

  return (
    <span className={className}>
      {trigger?.refresh_after_consolidation ? t("nextRefreshAuto") : t("nextRefreshManual")}
    </span>
  );
}
