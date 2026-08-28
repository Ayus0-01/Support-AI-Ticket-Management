type SufficiencyBadgeProps = {
  sufficient: boolean;
};

export default function SufficiencyBadge({ sufficient }: SufficiencyBadgeProps) {
  return (
    <span
      className={`inline-flex rounded-full px-3 py-1 text-xs font-bold uppercase tracking-wide ${
        sufficient
          ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300"
          : "bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300"
      }`}
    >
      {sufficient ? "Grounded KB context" : "Insufficient KB context"}
    </span>
  );
}
