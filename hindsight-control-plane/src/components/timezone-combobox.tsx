"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { Check, ChevronsUpDown } from "lucide-react";
import { useTranslations } from "next-intl";

import { Button } from "@/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { cn } from "@/lib/utils";
import {
  filterTimezoneOptions,
  getBrowserTimezone,
  getTimezoneOffset,
  mergeTimezoneChoices,
} from "@/lib/timezones";

type IntlWithSupportedValues = typeof Intl & {
  supportedValuesOf?: (key: "timeZone") => string[];
};

export function TimezoneCombobox({
  value,
  onChange,
}: {
  value: string;
  onChange: (value: string) => void;
}) {
  const t = useTranslations("mentalModels");
  const tCommon = useTranslations("common");
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [browserTimezone, setBrowserTimezone] = useState("UTC");
  const [supportedTimezones, setSupportedTimezones] = useState<string[]>([]);
  const listRef = useRef<HTMLDivElement>(null);

  // Build browser-dependent values after mount so SSR and client markup hydrate identically.
  useEffect(() => {
    const supportedValuesOf = (Intl as IntlWithSupportedValues).supportedValuesOf;
    setBrowserTimezone(getBrowserTimezone());
    setSupportedTimezones(supportedValuesOf ? supportedValuesOf("timeZone") : []);
  }, []);

  useEffect(() => {
    if (!search) {
      requestAnimationFrame(() => listRef.current?.scrollTo({ top: 0 }));
    }
  }, [search]);

  const options = useMemo(() => {
    const now = new Date();
    return mergeTimezoneChoices(supportedTimezones, browserTimezone, value).map((timezone) => ({
      timezone,
      offset: getTimezoneOffset(timezone, now),
    }));
  }, [browserTimezone, supportedTimezones, value]);
  const filteredOptions = useMemo(() => filterTimezoneOptions(options, search), [options, search]);
  const selected = options.find((option) => option.timezone === value);

  // The combobox is used inside a modal Dialog; modal mode keeps its portalled list
  // inside Radix's active scroll/focus layer so wheel events are not blocked.
  return (
    <Popover
      modal
      open={open}
      onOpenChange={(nextOpen) => {
        setOpen(nextOpen);
        if (nextOpen) setSearch("");
      }}
    >
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          aria-label={t("optionsRefreshTimezoneLabel")}
          className="w-full justify-between font-normal"
        >
          <span className="truncate">
            {value || "UTC"}
            {selected?.offset ? ` (${selected.offset})` : ""}
          </span>
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent
        className="w-[var(--radix-popover-trigger-width)] max-h-[min(360px,var(--radix-popover-content-available-height))] p-0"
        align="start"
        side="bottom"
        sideOffset={4}
        collisionPadding={12}
      >
        <Command shouldFilter={false}>
          <CommandInput value={search} onValueChange={setSearch} placeholder={tCommon("search")} />
          <CommandList
            ref={listRef}
            className="max-h-[min(312px,calc(var(--radix-popover-content-available-height)-48px))] overscroll-contain"
          >
            <CommandEmpty>{tCommon("noResults")}</CommandEmpty>
            <CommandGroup>
              {filteredOptions.map((option) => (
                <CommandItem
                  key={option.timezone}
                  value={option.timezone}
                  onSelect={() => {
                    onChange(option.timezone);
                    setOpen(false);
                  }}
                >
                  <Check
                    className={cn(
                      "h-4 w-4 shrink-0",
                      value === option.timezone ? "opacity-100" : "opacity-0"
                    )}
                  />
                  <span className="min-w-0 flex-1 truncate">{option.timezone}</span>
                  {option.offset && (
                    <span className="shrink-0 text-xs text-muted-foreground">{option.offset}</span>
                  )}
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}
