import type { ResolutionStep } from "../../services/resolutionService";

type DestructiveWarningProps = {
  steps: ResolutionStep[];
};

export default function DestructiveWarning({ steps }: DestructiveWarningProps) {
  const approvalSteps = steps.filter((step) => step.requires_approval);

  if (approvalSteps.length === 0) {
    return null;
  }

  return (
    <div
      className="rounded-2xl border border-amber-300 bg-amber-50 p-4 text-sm text-amber-900 dark:border-amber-800 dark:bg-amber-950/40 dark:text-amber-200"
      role="alert"
    >
      <p className="font-semibold">Approval required before continuing</p>
      <p className="mt-1 leading-6">
        {approvalSteps.length === 1
          ? "One recommended step requires agent approval."
          : `${approvalSteps.length} recommended steps require agent approval.`} Review the cited guidance and obtain the required approval before performing those actions.
      </p>
    </div>
  );
}
