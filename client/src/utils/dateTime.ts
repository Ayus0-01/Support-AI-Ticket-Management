const INDIA_TIME_ZONE = "Asia/Kolkata";

/**
 * Parse API timestamps consistently. MongoDB returns naive datetimes in UTC
 * by default, so ISO timestamps without an explicit offset are treated as UTC.
 */
export function parseDateTime(value?: string | Date | null): Date | null {
  if (!value) return null;

  if (value instanceof Date) {
    return Number.isNaN(value.getTime()) ? null : value;
  }

  const raw = value.trim();
  if (!raw) return null;

  const normalized = raw.includes("T")
    ? raw
    : raw.replace(/^(\d{4}-\d{2}-\d{2})\s+/, "$1T");
  const hasExplicitTimeZone = /(?:Z|[+-]\d{2}:?\d{2})$/i.test(normalized);
  const timestamp = new Date(
    /^\d{4}-\d{2}-\d{2}T/.test(normalized) && !hasExplicitTimeZone
      ? `${normalized}Z`
      : normalized,
  );

  return Number.isNaN(timestamp.getTime()) ? null : timestamp;
}

export function formatDateTime(
  value?: string | Date | null,
  options: Intl.DateTimeFormatOptions = {
    dateStyle: "short",
    timeStyle: "medium",
  },
): string {
  const date = parseDateTime(value);
  if (!date) return "—";

  return new Intl.DateTimeFormat("en-IN", {
    ...options,
    timeZone: INDIA_TIME_ZONE,
  }).format(date);
}

export function getIndiaDateKey(value?: string | Date | null): string | null {
  const date = parseDateTime(value);
  if (!date) return null;

  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: INDIA_TIME_ZONE,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(date);
  const year = parts.find(({ type }) => type === "year")?.value;
  const month = parts.find(({ type }) => type === "month")?.value;
  const day = parts.find(({ type }) => type === "day")?.value;
  return year && month && day ? `${year}-${month}-${day}` : null;
}
