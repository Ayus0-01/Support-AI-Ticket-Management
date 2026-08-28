import { useState } from "react";
import type { ResolutionCitation, ResolutionStep } from "../../services/resolutionService";
import CitationCard from "./CitationCard";

type StepChecklistProps = {
  steps: ResolutionStep[];
  citations: ResolutionCitation[];
};

export default function StepChecklist({ steps, citations }: StepChecklistProps) {
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(() => new Set());
  const orderedSteps = [...steps].sort((left, right) => left.order - right.order);

  if (orderedSteps.length === 0) {
    return null;
  }

  const toggleStep = (order: number) => {
    setCompletedSteps((current) => {
      const next = new Set(current);
      if (next.has(order)) {
        next.delete(order);
      } else {
        next.add(order);
      }
      return next;
    });
  };

  return (
    <ol className="space-y-4">
      {orderedSteps.map((step) => {
        const stepCitations = citations.filter((citation) => citation.step_order === step.order);
        const completed = completedSteps.has(step.order);

        return (
          <li key={`${step.order}-${step.instruction}`} className="rounded-2xl border border-slate-200 p-4 dark:border-gray-800 dark:bg-gray-900/50">
            <div className="flex items-start gap-3">
              <input
                id={`resolution-step-${step.order}`}
                type="checkbox"
                checked={completed}
                onChange={() => toggleStep(step.order)}
                className="mt-1 h-4 w-4 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"
              />
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <label htmlFor={`resolution-step-${step.order}`} className={`text-sm leading-6 ${completed ? "text-slate-500 line-through dark:text-gray-500" : "text-slate-800 dark:text-gray-100"}`}>
                    <span className="mr-2 font-semibold">{step.order}.</span>
                    {step.instruction}
                  </label>
                  {step.requires_approval && (
                    <span className="rounded-full bg-amber-100 px-2 py-0.5 text-[11px] font-bold uppercase tracking-wide text-amber-800 dark:bg-amber-950/60 dark:text-amber-300">
                      Approval required
                    </span>
                  )}
                </div>

                {stepCitations.length > 0 && (
                  <div className="mt-3 space-y-2">
                    {stepCitations.map((citation) => (
                      <CitationCard
                        key={`${citation.article_id}-${citation.chunk_index}-${citation.step_order}`}
                        citation={citation}
                      />
                    ))}
                  </div>
                )}
              </div>
            </div>
          </li>
        );
      })}
    </ol>
  );
}
