import { useEffect, useState } from "react";
import type { ResolutionResponse } from "../../services/resolutionService";

type EditAndSendDialogProps = {
  response: ResolutionResponse;
  busy: boolean;
  onCancel: () => void;
  onSubmit: (summary: string) => Promise<void> | void;
};

export default function EditAndSendDialog({
  response,
  busy,
  onCancel,
  onSubmit,
}: EditAndSendDialogProps) {
  const [summary, setSummary] = useState(response.summary);

  useEffect(() => {
    setSummary(response.summary);
  }, [response.id, response.summary]);

  const submit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await onSubmit(summary.trim());
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4" role="dialog" aria-modal="true" aria-labelledby="edit-send-title">
      <form onSubmit={submit} className="w-full max-w-2xl rounded-3xl bg-white p-6 shadow-xl dark:bg-gray-900">
        <h3 id="edit-send-title" className="text-lg font-bold text-slate-900 dark:text-white">Edit and send resolution</h3>
        <p className="mt-1 text-sm text-slate-600 dark:text-gray-400">
          You can refine the summary before sending. Cited troubleshooting steps stay unchanged to preserve their validated source grounding.
        </p>
        <label htmlFor="edited-resolution-summary" className="mt-5 block text-sm font-semibold text-slate-800 dark:text-gray-200">Resolution summary</label>
        <textarea
          id="edited-resolution-summary"
          value={summary}
          onChange={(event) => setSummary(event.target.value)}
          rows={5}
          disabled={busy}
          className="mt-2 w-full rounded-2xl border border-slate-300 px-3 py-2.5 text-sm text-slate-900 outline-none focus:border-blue-500 disabled:opacity-60 dark:border-gray-700 dark:bg-gray-950 dark:text-white"
        />
        <p className="mt-4 text-xs text-slate-500 dark:text-gray-400">{response.steps.length} cited troubleshooting {response.steps.length === 1 ? "step will" : "steps will"} be sent unchanged.</p>
        <div className="mt-6 flex flex-wrap justify-end gap-3">
          <button type="button" onClick={onCancel} disabled={busy} className="rounded-2xl border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 disabled:opacity-50 dark:border-gray-700 dark:text-gray-200">Cancel</button>
          <button type="submit" disabled={busy || !summary.trim()} className="rounded-2xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50">{busy ? "Sending..." : "Send edited resolution"}</button>
        </div>
      </form>
    </div>
  );
}
