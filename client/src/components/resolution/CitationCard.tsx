import { useState } from "react";
import type { ResolutionCitation } from "../../services/resolutionService";

type CitationCardProps = {
  citation: ResolutionCitation;
};

export default function CitationCard({ citation }: CitationCardProps) {
  const [expanded, setExpanded] = useState(false);
  const title = citation.article_title || citation.source || "Knowledge Base source";

  return (
    <div className="rounded-xl border border-blue-100 bg-blue-50/70 dark:border-blue-900/70 dark:bg-blue-950/20">
      <button
        type="button"
        onClick={() => setExpanded((current) => !current)}
        className="flex w-full items-start justify-between gap-3 px-3 py-2.5 text-left text-xs transition hover:bg-blue-100/60 dark:hover:bg-blue-900/30"
        aria-expanded={expanded}
      >
        <span>
          <span className="block font-semibold text-blue-900 dark:text-blue-200">{title}</span>
          {citation.section && (
            <span className="mt-0.5 block text-blue-700 dark:text-blue-300">{citation.section}</span>
          )}
        </span>
        <span className="shrink-0 font-semibold text-blue-700 dark:text-blue-300">
          {expanded ? "Hide source" : "View source"}
        </span>
      </button>

      {expanded && (
        <div className="border-t border-blue-100 px-3 py-3 text-xs leading-5 text-slate-700 dark:border-blue-900/70 dark:text-slate-300">
          {citation.source && <p className="font-mono text-[11px] text-slate-500 dark:text-slate-400">{citation.source}</p>}
          {citation.snippet ? (
            <p className="mt-2 whitespace-pre-wrap">{citation.snippet}</p>
          ) : (
            <p className="mt-2 text-slate-500 dark:text-slate-400">No source excerpt is available for this citation.</p>
          )}
        </div>
      )}
    </div>
  );
}
