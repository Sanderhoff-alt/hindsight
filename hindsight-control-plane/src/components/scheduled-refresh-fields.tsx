"use client";

import { Info } from "lucide-react";
import { useTranslations } from "next-intl";

import { Input } from "@/components/ui/input";
import { CronSchedulePreview } from "./cron-schedule-preview";
import { TimezoneCombobox } from "./timezone-combobox";

/**
 * The cron expression + IANA timezone + live preview shown when a mental
 * model's refresh trigger is set to "scheduled". Shared by the create and
 * update dialogs in mental-models-view.tsx, which otherwise duplicated this
 * block verbatim.
 */
export function ScheduledRefreshFields({
  cron,
  timezone,
  onCronChange,
  onTimezoneChange,
}: {
  cron: string;
  timezone: string;
  onCronChange: (value: string) => void;
  onTimezoneChange: (value: string) => void;
}) {
  const t = useTranslations("mentalModels");

  return (
    <div className="space-y-2">
      <div className="grid gap-3 sm:grid-cols-[minmax(0,1fr)_minmax(14rem,1fr)]">
        <div className="space-y-2">
          <label className="text-sm font-medium text-foreground">
            {t("optionsRefreshCronLabel")}
          </label>
          <Input
            value={cron}
            onChange={(e) => onCronChange(e.target.value)}
            placeholder={t("optionsRefreshCronPlaceholder")}
          />
        </div>
        <div className="space-y-2">
          <div className="flex items-center gap-1">
            <label className="text-sm font-medium text-foreground">
              {t("optionsRefreshTimezoneLabel")}
            </label>
            <span
              title={t("optionsRefreshTimezoneInfo")}
              aria-label={t("optionsRefreshTimezoneInfo")}
            >
              <Info className="h-3.5 w-3.5 text-muted-foreground" />
            </span>
          </div>
          <TimezoneCombobox value={timezone} onChange={onTimezoneChange} />
        </div>
      </div>
      <p className="text-xs text-muted-foreground">{t("optionsRefreshCronDescription")}</p>
      <CronSchedulePreview cron={cron} timezone={timezone} />
    </div>
  );
}
