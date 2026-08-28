import { ChangeEvent, useCallback, useEffect, useRef, useState } from "react";
import {
  BookOpen,
  ChevronRight,
  Loader2,
  Plus,
  RefreshCw,
  Search,
  Upload,
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import {
  createKnowledgeArticle,
  getIngestionStatus,
  getKnowledgeArticle,
  getKnowledgeArticles,
  getKnowledgeGaps,
  previewKnowledgeArticleChunks,
  publishKnowledgeArticle,
  searchKnowledgeBase,
  updateKnowledgeArticle,
  uploadKnowledgeDocuments,
  type ChunkPreview,
  type IngestionJob,
  type KnowledgeArticle,
  type KnowledgeArticleDetail,
  type KnowledgeArticleInput,
  type KnowledgeGap,
  type KnowledgeSearchResult,
} from "../../services/knowledgeBaseService";

type Tab = "articles" | "search" | "ingestion" | "gaps";

type EditorState = KnowledgeArticleInput & {
  change_note: string;
};

const newEditor = (): EditorState => ({
  title: "",
  slug: "",
  category: "",
  sub_category: "",
  tags: [],
  content: "",
  source_system: "MANUAL",
  source_url: "",
  visible_to_departments: [],
  is_internal_only: false,
  change_note: "",
});

const toEditor = (article: KnowledgeArticleDetail): EditorState => ({
  title: article.title,
  slug: article.slug,
  category: article.category,
  sub_category: article.sub_category,
  tags: article.tags ?? [],
  content: article.content,
  source_system: article.source_system as EditorState["source_system"],
  source_url: article.source_url ?? "",
  visible_to_departments: article.visible_to_departments ?? [],
  is_internal_only: article.is_internal_only,
  change_note: "",
});

const getErrorMessage = (error: unknown, fallback: string) => {
  if (!error || typeof error !== "object") {
    return fallback;
  }

  const candidate = error as {
    message?: string;
    response?: { data?: { message?: string; detail?: string } };
  };

  return candidate.response?.data?.message || candidate.response?.data?.detail || candidate.message || fallback;
};

const splitEntries = (value: string) => value
  .split(",")
  .map((entry) => entry.trim())
  .filter(Boolean);

const slugFromTitle = (value: string) => value
  .toLowerCase()
  .trim()
  .replace(/[^a-z0-9]+/g, "-")
  .replace(/(^-|-$)/g, "");

const formatDate = (value?: string | null) => {
  if (!value) {
    return "—";
  }

  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
};

const isTerminalJob = (status?: string) => ["COMPLETED", "COMPLETED_WITH_ERRORS", "FAILED"].includes(status || "");

function StatusPill({ status }: { status: string }) {
  const published = status === "PUBLISHED" || status === "COMPLETED";
  const warning = status === "DRAFT" || status === "COMPLETED_WITH_ERRORS";
  const classes = published
    ? "bg-emerald-100 text-emerald-800"
    : warning
      ? "bg-amber-100 text-amber-800"
      : "bg-slate-100 text-slate-700";

  return <span className={`rounded-full px-2.5 py-1 text-[11px] font-bold tracking-wide ${classes}`}>{status.replace(/_/g, " ")}</span>;
}

function ArticleList({
  articles,
  selectedId,
  loading,
  error,
  isDark,
  onSelect,
  onReload,
}: {
  articles: KnowledgeArticle[];
  selectedId: string | null;
  loading: boolean;
  error: string;
  isDark: boolean;
  onSelect: (id: string) => void;
  onReload: () => void;
}) {
  if (loading) {
    return <div className="flex items-center gap-2 py-8 text-sm text-slate-500"><Loader2 className="h-4 w-4 animate-spin" /> Loading articles…</div>;
  }

  if (error) {
    return (
      <div className="rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-800">
        <p>{error}</p>
        <button type="button" onClick={onReload} className="mt-3 font-semibold underline">Try again</button>
      </div>
    );
  }

  if (articles.length === 0) {
    return <div className={`rounded-2xl border border-dashed p-6 text-sm ${isDark ? "border-gray-700 text-gray-400" : "border-slate-300 text-slate-500"}`}>No knowledge articles are available for your access level yet.</div>;
  }

  return (
    <div className="space-y-2">
      {articles.map((article) => {
        const active = article.id === selectedId;
        return (
          <button
            type="button"
            key={article.id}
            onClick={() => onSelect(article.id)}
            className={`w-full rounded-2xl border p-4 text-left transition ${active
              ? "border-blue-500 bg-blue-50"
              : isDark
                ? "border-gray-800 bg-gray-900 hover:border-gray-700"
                : "border-gray-200 bg-white hover:border-blue-300"
            }`}
          >
            <div className="flex items-start gap-3">
              <div className="mt-0.5 rounded-xl bg-blue-600 p-2 text-white"><BookOpen className="h-4 w-4" /></div>
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <p className={`truncate text-sm font-semibold ${isDark ? "text-white" : "text-slate-900"}`}>{article.title}</p>
                  <StatusPill status={article.status} />
                </div>
                <p className={`mt-1 text-xs ${isDark ? "text-gray-400" : "text-slate-500"}`}>{article.category} · {article.sub_category} · v{article.version}</p>
                <p className={`mt-1 text-xs ${article.index_error ? "text-red-600" : isDark ? "text-gray-500" : "text-slate-500"}`}>
                  {article.index_error ? `Index error: ${article.index_error}` : `${article.chunk_count} chunks · indexed version ${article.indexed_version ?? "not indexed"}`}
                </p>
              </div>
              <ChevronRight className={`mt-2 h-4 w-4 shrink-0 ${isDark ? "text-gray-600" : "text-slate-300"}`} />
            </div>
          </button>
        );
      })}
    </div>
  );
}

function ArticleReader({ article, isDark }: { article: KnowledgeArticleDetail; isDark: boolean }) {
  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="flex flex-wrap items-center gap-2"><StatusPill status={article.status} /> {article.is_internal_only && <span className="rounded-full bg-purple-100 px-2.5 py-1 text-[11px] font-bold tracking-wide text-purple-800">INTERNAL ONLY</span>}</div>
          <h3 className={`mt-3 text-xl font-bold ${isDark ? "text-white" : "text-slate-900"}`}>{article.title}</h3>
          <p className={`mt-1 text-sm ${isDark ? "text-gray-400" : "text-slate-500"}`}>{article.category} · {article.sub_category} · version {article.version}</p>
        </div>
        <div className={`text-right text-xs ${isDark ? "text-gray-500" : "text-slate-500"}`}>
          <p>Updated {formatDate(article.updated_at)}</p>
          <p>{article.chunk_count} chunks · indexed v{article.indexed_version ?? "—"}</p>
        </div>
      </div>
      {article.tags.length > 0 && <div className="flex flex-wrap gap-2">{article.tags.map((tag) => <span key={tag} className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-700">{tag}</span>)}</div>}
      <div className={`whitespace-pre-wrap rounded-2xl border p-5 text-sm leading-7 ${isDark ? "border-gray-800 bg-gray-950 text-gray-200" : "border-slate-200 bg-slate-50 text-slate-700"}`}>{article.content}</div>
      {article.source_url && <a href={article.source_url} target="_blank" rel="noreferrer" className="text-sm font-semibold text-blue-600 underline">Open source reference</a>}
    </div>
  );
}

function ArticleEditor({
  articleId,
  editor,
  isSaving,
  isPublishing,
  isPreviewing,
  isDark,
  onChange,
  onSave,
  onPublish,
  onPreview,
}: {
  articleId: string | null;
  editor: EditorState;
  isSaving: boolean;
  isPublishing: boolean;
  isPreviewing: boolean;
  isDark: boolean;
  onChange: (patch: Partial<EditorState>) => void;
  onSave: () => void;
  onPublish: () => void;
  onPreview: () => void;
}) {
  const field = `mt-1 w-full rounded-xl border px-3 py-2 text-sm outline-none transition focus:border-blue-500 ${isDark ? "border-gray-700 bg-gray-950 text-white" : "border-slate-300 bg-white text-slate-900"}`;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className={`text-sm font-bold ${isDark ? "text-white" : "text-slate-900"}`}>{articleId ? "Edit knowledge article" : "New knowledge article"}</p>
          <p className={`mt-1 text-xs ${isDark ? "text-gray-400" : "text-slate-500"}`}>Article changes are versioned by the backend. Publishing uses the latest saved version.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          {articleId && <button type="button" disabled={isPreviewing} onClick={onPreview} className="rounded-full border border-blue-200 px-3 py-2 text-xs font-bold text-blue-700 disabled:opacity-60">{isPreviewing ? "Preparing…" : "Preview chunks"}</button>}
          {articleId && <button type="button" disabled={isPublishing} onClick={onPublish} className="rounded-full bg-emerald-600 px-3 py-2 text-xs font-bold text-white disabled:opacity-60">{isPublishing ? "Publishing…" : "Publish"}</button>}
          <button type="button" disabled={isSaving} onClick={onSave} className="rounded-full bg-blue-600 px-3 py-2 text-xs font-bold text-white disabled:opacity-60">{isSaving ? "Saving…" : articleId ? "Save changes" : "Create draft"}</button>
        </div>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <label className="text-sm font-medium">Title<input value={editor.title} onChange={(event) => onChange({ title: event.target.value, slug: editor.slug || slugFromTitle(event.target.value) })} className={field} /></label>
        <label className="text-sm font-medium">Slug<input value={editor.slug} onChange={(event) => onChange({ slug: event.target.value })} className={field} placeholder="vpn-connectivity-troubleshooting" /></label>
        <label className="text-sm font-medium">Category<input value={editor.category} onChange={(event) => onChange({ category: event.target.value })} className={field} /></label>
        <label className="text-sm font-medium">Sub-category<input value={editor.sub_category} onChange={(event) => onChange({ sub_category: event.target.value })} className={field} /></label>
        <label className="text-sm font-medium">Tags (comma-separated)<input value={editor.tags.join(", ")} onChange={(event) => onChange({ tags: splitEntries(event.target.value) })} className={field} placeholder="vpn, connectivity" /></label>
        <label className="text-sm font-medium">Source system<select value={editor.source_system} onChange={(event) => onChange({ source_system: event.target.value as EditorState["source_system"] })} className={field}><option value="MANUAL">Manual</option><option value="CONFLUENCE">Confluence</option><option value="SHAREPOINT">SharePoint</option><option value="UPLOAD">Upload</option></select></label>
        <label className="text-sm font-medium md:col-span-2">Source URL (optional)<input type="url" value={editor.source_url ?? ""} onChange={(event) => onChange({ source_url: event.target.value })} className={field} /></label>
        <label className="text-sm font-medium md:col-span-2">Visible departments (comma-separated)<input value={editor.visible_to_departments.join(", ")} onChange={(event) => onChange({ visible_to_departments: splitEntries(event.target.value) })} className={field} placeholder="Finance, IT" /></label>
      </div>
      <label className="flex items-center gap-2 text-sm font-medium"><input type="checkbox" checked={editor.is_internal_only} onChange={(event) => onChange({ is_internal_only: event.target.checked })} /> Internal-only content</label>
      <label className="block text-sm font-medium">Content<textarea value={editor.content} onChange={(event) => onChange({ content: event.target.value })} className={`${field} min-h-72 resize-y font-mono leading-6`} placeholder="Write article content with meaningful headings for chunking." /></label>
      {articleId && <label className="block text-sm font-medium">Change note (optional)<input value={editor.change_note} onChange={(event) => onChange({ change_note: event.target.value })} className={field} placeholder="Explain this revision" /></label>}
    </div>
  );
}

function ChunkPreviewList({ chunks, isDark }: { chunks: ChunkPreview[]; isDark: boolean }) {
  if (chunks.length === 0) {
    return null;
  }

  return (
    <div className={`rounded-2xl border p-4 ${isDark ? "border-gray-800 bg-gray-950" : "border-slate-200 bg-slate-50"}`}>
      <p className={`text-sm font-bold ${isDark ? "text-white" : "text-slate-900"}`}>Chunk preview</p>
      <p className={`mt-1 text-xs ${isDark ? "text-gray-400" : "text-slate-500"}`}>This preview is generated by the backend’s live heading-aware chunking service.</p>
      <div className="mt-4 max-h-96 space-y-3 overflow-y-auto pr-1">
        {chunks.map((chunk) => <div key={`${chunk.index}-${chunk.heading_path}`} className={`rounded-xl border p-3 ${isDark ? "border-gray-800 bg-gray-900" : "border-slate-200 bg-white"}`}><div className="flex flex-wrap justify-between gap-2 text-xs"><span className="font-bold text-blue-600">#{chunk.index + 1} {chunk.heading_path || "Article content"}</span><span className={isDark ? "text-gray-400" : "text-slate-500"}>{chunk.token_count} tokens</span></div><p className={`mt-2 whitespace-pre-wrap text-xs leading-5 ${isDark ? "text-gray-300" : "text-slate-700"}`}>{chunk.content}</p></div>)}
      </div>
    </div>
  );
}

function IngestionView({ isDark }: { isDark: boolean }) {
  const [files, setFiles] = useState<File[]>([]);
  const [metadata, setMetadata] = useState({ category: "", sub_category: "", visible_to_departments: "", is_internal_only: false });
  const [job, setJob] = useState<IngestionJob | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);
  const field = `mt-1 w-full rounded-xl border px-3 py-2 text-sm outline-none focus:border-blue-500 ${isDark ? "border-gray-700 bg-gray-950 text-white" : "border-slate-300 bg-white text-slate-900"}`;
  const pollingJobId = job?.job_id;
  const pollingJobStatus = job?.status;

  useEffect(() => {
    if (!pollingJobId || isTerminalJob(pollingJobStatus)) {
      return undefined;
    }

    const timer = window.setInterval(() => {
      void getIngestionStatus(pollingJobId)
        .then((nextJob) => setJob(nextJob))
        .catch((statusError) => setError(getErrorMessage(statusError, "Could not refresh ingestion status.")));
    }, 2000);

    return () => window.clearInterval(timer);
  }, [pollingJobId, pollingJobStatus]);

  const selectFiles = (event: ChangeEvent<HTMLInputElement>) => {
    const nextFiles = Array.from(event.target.files ?? []);
    if (nextFiles.length > 50) {
      setError("A maximum of 50 files can be submitted at once.");
      return;
    }
    setError("");
    setFiles(nextFiles);
  };

  const submit = async () => {
    if (files.length === 0) {
      setError("Choose one or more supported documents first.");
      return;
    }
    try {
      setBusy(true);
      setError("");
      const startedJob = await uploadKnowledgeDocuments(files, {
        category: metadata.category || undefined,
        sub_category: metadata.sub_category || undefined,
        visible_to_departments: splitEntries(metadata.visible_to_departments),
        is_internal_only: metadata.is_internal_only,
      });
      setJob(startedJob);
    } catch (uploadError) {
      setError(getErrorMessage(uploadError, "Documents could not be submitted for ingestion."));
    } finally {
      setBusy(false);
    }
  };

  const refresh = async () => {
    if (!job) {
      return;
    }
    try {
      setError("");
      setJob(await getIngestionStatus(job.job_id));
    } catch (statusError) {
      setError(getErrorMessage(statusError, "Could not refresh ingestion status."));
    }
  };

  return (
    <div className="grid gap-6 xl:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
      <section className={`rounded-3xl border p-6 ${isDark ? "border-gray-800 bg-gray-900" : "border-gray-200 bg-white"}`}>
        <div className="flex items-center gap-3"><div className="rounded-xl bg-blue-600 p-2.5 text-white"><Upload className="h-5 w-5" /></div><div><h3 className={`font-bold ${isDark ? "text-white" : "text-slate-900"}`}>Bulk document ingestion</h3><p className={`text-xs ${isDark ? "text-gray-400" : "text-slate-500"}`}>Files are sent to the authenticated backend ingestion service.</p></div></div>
        <div className="mt-6 space-y-4">
          <label className="block text-sm font-medium">Files<input ref={inputRef} type="file" multiple accept=".md,.markdown,.html,.htm,.docx,.pdf" onChange={selectFiles} className={field} /></label>
          <p className={`text-xs ${isDark ? "text-gray-400" : "text-slate-500"}`}>Up to 50 Markdown, HTML, DOCX, or PDF files; 10 MB per file.</p>
          {files.length > 0 && <ul className={`max-h-36 space-y-1 overflow-y-auto rounded-xl p-3 text-xs ${isDark ? "bg-gray-950 text-gray-300" : "bg-slate-50 text-slate-700"}`}>{files.map((file) => <li key={`${file.name}-${file.lastModified}`} className="flex justify-between gap-3"><span className="truncate">{file.name}</span><span>{Math.ceil(file.size / 1024)} KB</span></li>)}</ul>}
          <div className="grid gap-4 sm:grid-cols-2"><label className="text-sm font-medium">Category<input value={metadata.category} onChange={(event) => setMetadata((current) => ({ ...current, category: event.target.value }))} className={field} /></label><label className="text-sm font-medium">Sub-category<input value={metadata.sub_category} onChange={(event) => setMetadata((current) => ({ ...current, sub_category: event.target.value }))} className={field} /></label></div>
          <label className="block text-sm font-medium">Visible departments<input value={metadata.visible_to_departments} onChange={(event) => setMetadata((current) => ({ ...current, visible_to_departments: event.target.value }))} className={field} placeholder="Finance, IT" /></label>
          <label className="flex items-center gap-2 text-sm font-medium"><input type="checkbox" checked={metadata.is_internal_only} onChange={(event) => setMetadata((current) => ({ ...current, is_internal_only: event.target.checked }))} /> Internal-only content</label>
          {error && <p className="rounded-xl bg-red-50 p-3 text-sm text-red-800">{error}</p>}
          <button type="button" onClick={submit} disabled={busy} className="inline-flex items-center gap-2 rounded-full bg-blue-600 px-4 py-2.5 text-sm font-bold text-white disabled:opacity-60"><Upload className="h-4 w-4" />{busy ? "Submitting…" : "Ingest documents"}</button>
        </div>
      </section>
      <section className={`rounded-3xl border p-6 ${isDark ? "border-gray-800 bg-gray-900" : "border-gray-200 bg-white"}`}>
        <div className="flex items-center justify-between gap-3"><div><h3 className={`font-bold ${isDark ? "text-white" : "text-slate-900"}`}>Ingestion status</h3><p className={`mt-1 text-xs ${isDark ? "text-gray-400" : "text-slate-500"}`}>Progress and document-level failures are reported by the job.</p></div>{job && <button type="button" onClick={refresh} className="rounded-full border border-slate-300 p-2 text-slate-600"><RefreshCw className="h-4 w-4" /></button>}</div>
        {!job ? <div className={`mt-6 rounded-2xl border border-dashed p-5 text-sm ${isDark ? "border-gray-700 text-gray-400" : "border-slate-300 text-slate-500"}`}>Submit a document batch to inspect its live ingestion result here.</div> : <div className="mt-6 space-y-5"><div className="flex flex-wrap items-center justify-between gap-3"><StatusPill status={job.status} /><span className={`text-xs ${isDark ? "text-gray-400" : "text-slate-500"}`}>Job {job.job_id}</span></div><div className="grid grid-cols-2 gap-3 sm:grid-cols-3">{Object.entries(job.progress ?? {}).map(([label, value]) => <div key={label} className={`rounded-xl p-3 ${isDark ? "bg-gray-950" : "bg-slate-50"}`}><p className={`text-[11px] uppercase tracking-wide ${isDark ? "text-gray-500" : "text-slate-500"}`}>{label.replace(/_/g, " ")}</p><p className={`mt-1 text-lg font-bold ${isDark ? "text-white" : "text-slate-900"}`}>{String(value)}</p></div>)}</div>{job.errors?.length > 0 && <div className="rounded-2xl border border-red-200 bg-red-50 p-4"><p className="text-sm font-bold text-red-800">Document failures</p><ul className="mt-2 space-y-2 text-sm text-red-800">{job.errors.map((item, index) => <li key={`${item.document}-${index}`}><strong>{item.document || "Document"}</strong>{item.stage ? ` (${item.stage})` : ""}: {item.message || "Unknown error"}</li>)}</ul></div>}{job.results && job.results.length > 0 && <div className="space-y-2"><p className={`text-sm font-bold ${isDark ? "text-white" : "text-slate-900"}`}>Processed documents</p>{job.results.map((item, index) => <div key={`${item.article_id}-${index}`} className={`rounded-xl border p-3 text-sm ${isDark ? "border-gray-800 bg-gray-950 text-gray-300" : "border-slate-200 bg-slate-50 text-slate-700"}`}><p className="font-semibold">{item.title || item.path || "Document"}</p><p className="mt-1 text-xs">{item.chunk_count ?? 0} chunks · {item.created ? "created" : "updated"} · {item.status || "processed"}</p></div>)}</div>}</div>}
      </section>
    </div>
  );
}

function SearchView({ isDark, canManage, onOpenArticle }: { isDark: boolean; canManage: boolean; onOpenArticle: (articleId: string) => void }) {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("");
  const [includeInternal, setIncludeInternal] = useState(false);
  const [results, setResults] = useState<KnowledgeSearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const field = `w-full rounded-xl border px-3 py-2.5 text-sm outline-none focus:border-blue-500 ${isDark ? "border-gray-700 bg-gray-950 text-white" : "border-slate-300 bg-white text-slate-900"}`;

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!query.trim()) {
      setError("Enter a question or issue description to search the Knowledge Base.");
      return;
    }
    try {
      setLoading(true);
      setError("");
      setResults(await searchKnowledgeBase({ query: query.trim(), category: category.trim() || undefined, top_k: 5, include_internal: canManage && includeInternal }));
    } catch (searchError) {
      setError(getErrorMessage(searchError, "Knowledge Base search failed."));
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div><h3 className={`text-xl font-bold ${isDark ? "text-white" : "text-slate-900"}`}>Self-help semantic search</h3><p className={`mt-2 text-sm ${isDark ? "text-gray-400" : "text-slate-500"}`}>Search results come from the existing hybrid retrieval and reranking pipeline.</p></div>
      <form onSubmit={submit} className={`rounded-3xl border p-5 ${isDark ? "border-gray-800 bg-gray-900" : "border-gray-200 bg-white"}`}><div className="flex flex-col gap-3 sm:flex-row"><label className="sr-only" htmlFor="kb-search">Search Knowledge Base</label><input id="kb-search" value={query} onChange={(event) => setQuery(event.target.value)} className={`flex-1 ${field}`} placeholder="Describe the issue or ask a support question" /><button type="submit" disabled={loading} className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-bold text-white disabled:opacity-60"><Search className="h-4 w-4" />{loading ? "Searching…" : "Search"}</button></div><div className="mt-3 flex flex-wrap items-center gap-3"><input value={category} onChange={(event) => setCategory(event.target.value)} className={`max-w-xs ${field}`} placeholder="Optional category" />{canManage && <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={includeInternal} onChange={(event) => setIncludeInternal(event.target.checked)} /> Include internal articles</label>}</div></form>
      {error && <div className="rounded-2xl bg-red-50 p-4 text-sm text-red-800">{error}</div>}
      {!loading && !error && results.length === 0 && <div className={`rounded-2xl border border-dashed p-6 text-sm ${isDark ? "border-gray-700 text-gray-400" : "border-slate-300 text-slate-500"}`}>Search published knowledge to find grounded help articles.</div>}
      <div className="space-y-3">{results.map((result, index) => <button type="button" key={`${result.article_id}-${result.chunk_index ?? index}`} onClick={() => onOpenArticle(result.article_id)} className={`w-full rounded-2xl border p-5 text-left ${isDark ? "border-gray-800 bg-gray-900 hover:border-gray-700" : "border-gray-200 bg-white hover:border-blue-300"}`}><div className="flex items-start justify-between gap-3"><div><p className={`font-bold ${isDark ? "text-white" : "text-slate-900"}`}>{result.article_title || "Knowledge article"}</p><p className={`mt-1 text-xs ${isDark ? "text-gray-400" : "text-slate-500"}`}>{result.category || "Uncategorised"}{result.sub_category ? ` · ${result.sub_category}` : ""}{result.heading_path ? ` · ${result.heading_path}` : ""}</p></div><ChevronRight className="h-4 w-4 shrink-0 text-blue-600" /></div>{result.content && <p className={`mt-3 line-clamp-3 whitespace-pre-wrap text-sm leading-6 ${isDark ? "text-gray-300" : "text-slate-700"}`}>{result.content}</p>}</button>)}</div>
    </div>
  );
}

function GapsView({ isDark }: { isDark: boolean }) {
  const [gaps, setGaps] = useState<KnowledgeGap[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = async () => {
    try {
      setLoading(true);
      setError("");
      setGaps(await getKnowledgeGaps());
    } catch (gapError) {
      setError(getErrorMessage(gapError, "Knowledge gaps could not be loaded."));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void load(); }, []);

  if (loading) {
    return <div className="flex items-center gap-2 py-8 text-sm text-slate-500"><Loader2 className="h-4 w-4 animate-spin" /> Loading knowledge gaps…</div>;
  }

  if (error) {
    return <div className="rounded-2xl bg-red-50 p-4 text-sm text-red-800"><p>{error}</p><button type="button" onClick={() => void load()} className="mt-3 font-semibold underline">Try again</button></div>;
  }

  return (
    <div className="space-y-4"><div className="flex items-center justify-between"><div><h3 className={`text-xl font-bold ${isDark ? "text-white" : "text-slate-900"}`}>Knowledge gaps</h3><p className={`mt-1 text-sm ${isDark ? "text-gray-400" : "text-slate-500"}`}>Recurring insufficient-context requests recorded by the backend.</p></div><button type="button" onClick={() => void load()} className="rounded-full border border-slate-300 p-2 text-slate-600"><RefreshCw className="h-4 w-4" /></button></div>{gaps.length === 0 ? <div className={`rounded-2xl border border-dashed p-6 text-sm ${isDark ? "border-gray-700 text-gray-400" : "border-slate-300 text-slate-500"}`}>No open knowledge gaps were reported.</div> : <div className="space-y-3">{gaps.map((gap, index) => <div key={`${String(gap._id ?? gap.query ?? index)}`} className={`rounded-2xl border p-5 ${isDark ? "border-gray-800 bg-gray-900" : "border-gray-200 bg-white"}`}><div className="flex flex-wrap items-start justify-between gap-3"><div><p className={`font-semibold ${isDark ? "text-white" : "text-slate-900"}`}>{String(gap.query || gap.normalized_query || "Unspecified request")}</p><p className={`mt-1 text-xs ${isDark ? "text-gray-400" : "text-slate-500"}`}>{gap.category ? `Category: ${String(gap.category)}` : "No category recorded"}{gap.department ? ` · ${String(gap.department)}` : ""}</p></div><span className="rounded-full bg-amber-100 px-3 py-1 text-xs font-bold text-amber-800">{String(gap.occurrence_count ?? 1)} occurrences</span></div><p className={`mt-3 text-xs ${isDark ? "text-gray-500" : "text-slate-500"}`}>Last seen {formatDate(String(gap.last_seen_at ?? gap.updated_at ?? ""))}</p></div>)}</div>}</div>
  );
}

export default function KnowledgeBasePage({ isDark }: { isDark: boolean }) {
  const { can } = useAuth();
  const canManage = can("ADMIN_SETTINGS");
  const [tab, setTab] = useState<Tab>("articles");
  const [articles, setArticles] = useState<KnowledgeArticle[]>([]);
  const [articlesLoading, setArticlesLoading] = useState(true);
  const [articlesError, setArticlesError] = useState("");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<KnowledgeArticleDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState("");
  const [editor, setEditor] = useState<EditorState | null>(null);
  const [actionError, setActionError] = useState("");
  const [saving, setSaving] = useState(false);
  const [publishing, setPublishing] = useState(false);
  const [previewing, setPreviewing] = useState(false);
  const [chunks, setChunks] = useState<ChunkPreview[]>([]);

  const loadArticles = useCallback(async () => {
    try {
      setArticlesLoading(true);
      setArticlesError("");
      setArticles(await getKnowledgeArticles(canManage));
    } catch (loadError) {
      setArticlesError(getErrorMessage(loadError, "Knowledge Base articles could not be loaded."));
    } finally {
      setArticlesLoading(false);
    }
  }, [canManage]);

  useEffect(() => { void loadArticles(); }, [loadArticles]);

  const openArticle = async (articleId: string) => {
    try {
      setSelectedId(articleId);
      setDetailLoading(true);
      setDetailError("");
      setActionError("");
      setChunks([]);
      const article = await getKnowledgeArticle(articleId);
      setDetail(article);
      setEditor(canManage ? toEditor(article) : null);
    } catch (openError) {
      setDetail(null);
      setEditor(null);
      setDetailError(getErrorMessage(openError, "Knowledge article could not be loaded."));
    } finally {
      setDetailLoading(false);
    }
  };

  const startNewArticle = () => {
    setSelectedId(null);
    setDetail(null);
    setDetailError("");
    setActionError("");
    setChunks([]);
    setEditor(newEditor());
  };

  const saveArticle = async () => {
    if (!editor) {
      return;
    }
    if (!editor.title.trim() || !editor.slug.trim() || !editor.category.trim() || !editor.sub_category.trim() || !editor.content.trim()) {
      setActionError("Title, slug, category, sub-category, and content are required before saving.");
      return;
    }
    try {
      setSaving(true);
      setActionError("");
      const payload: KnowledgeArticleInput = {
        title: editor.title.trim(),
        slug: editor.slug.trim(),
        category: editor.category.trim(),
        sub_category: editor.sub_category.trim(),
        tags: editor.tags,
        content: editor.content,
        source_system: editor.source_system,
        source_url: editor.source_url?.trim() || null,
        visible_to_departments: editor.visible_to_departments,
        is_internal_only: editor.is_internal_only,
      };
      const saved = selectedId
        ? await updateKnowledgeArticle(selectedId, { ...payload, change_note: editor.change_note.trim() || undefined })
        : await createKnowledgeArticle(payload);
      setSelectedId(saved.id);
      setDetail(saved);
      setEditor(toEditor(saved));
      await loadArticles();
    } catch (saveError) {
      setActionError(getErrorMessage(saveError, "Knowledge article could not be saved."));
    } finally {
      setSaving(false);
    }
  };

  const publishArticle = async () => {
    if (!selectedId) {
      setActionError("Create and save the draft before publishing it.");
      return;
    }
    try {
      setPublishing(true);
      setActionError("");
      const published = await publishKnowledgeArticle(selectedId, editor?.change_note.trim());
      setDetail(published);
      setEditor(toEditor(published));
      setChunks([]);
      await loadArticles();
    } catch (publishError) {
      setActionError(getErrorMessage(publishError, "Knowledge article could not be published."));
    } finally {
      setPublishing(false);
    }
  };

  const previewChunks = async () => {
    if (!selectedId || !editor?.content.trim()) {
      setActionError("Save a draft with content before requesting a chunk preview.");
      return;
    }
    try {
      setPreviewing(true);
      setActionError("");
      setChunks(await previewKnowledgeArticleChunks(selectedId, editor.content, editor.title));
    } catch (previewError) {
      setActionError(getErrorMessage(previewError, "Chunk preview could not be generated."));
    } finally {
      setPreviewing(false);
    }
  };

  const openSearchArticle = (articleId: string) => {
    setTab("articles");
    void openArticle(articleId);
  };

  const tabs: Array<{ id: Tab; label: string; admin?: boolean }> = [
    { id: "articles", label: "Articles" },
    { id: "search", label: "Self-help search" },
    { id: "ingestion", label: "Ingestion", admin: true },
    { id: "gaps", label: "KB gaps", admin: true },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end"><div><p className={`text-sm font-semibold uppercase tracking-[0.22em] ${isDark ? "text-blue-400" : "text-blue-600"}`}>M2 Knowledge Base</p><h2 className={`mt-1 text-2xl font-bold ${isDark ? "text-white" : "text-slate-900"}`}>Knowledge Base</h2><p className={`mt-2 max-w-2xl text-sm ${isDark ? "text-gray-400" : "text-slate-500"}`}>Browse published support knowledge, search semantically, and—when authorised—manage the live article and ingestion workflow.</p></div>{canManage && <button type="button" onClick={startNewArticle} className="inline-flex items-center justify-center gap-2 rounded-full bg-blue-600 px-4 py-2.5 text-sm font-bold text-white"><Plus className="h-4 w-4" />New article</button>}</div>
      <div className="flex flex-wrap gap-2 border-b border-slate-200 pb-3">{tabs.filter((item) => !item.admin || canManage).map((item) => <button type="button" key={item.id} onClick={() => setTab(item.id)} className={`rounded-full px-4 py-2 text-sm font-bold transition ${tab === item.id ? "bg-blue-600 text-white" : isDark ? "bg-gray-900 text-gray-300 hover:bg-gray-800" : "bg-white text-slate-600 hover:bg-slate-100"}`}>{item.label}</button>)}</div>
      {tab === "search" && <SearchView isDark={isDark} canManage={canManage} onOpenArticle={openSearchArticle} />}
      {tab === "ingestion" && canManage && <IngestionView isDark={isDark} />}
      {tab === "gaps" && canManage && <GapsView isDark={isDark} />}
      {tab === "articles" && <div className="grid gap-6 xl:grid-cols-[minmax(300px,0.75fr)_minmax(0,1.25fr)]"><section><div className="mb-3 flex items-center justify-between"><p className={`text-sm font-bold ${isDark ? "text-white" : "text-slate-900"}`}>Articles</p><button type="button" onClick={() => void loadArticles()} className="rounded-full border border-slate-300 p-2 text-slate-600"><RefreshCw className="h-4 w-4" /></button></div><ArticleList articles={articles} selectedId={selectedId} loading={articlesLoading} error={articlesError} isDark={isDark} onSelect={(articleId) => void openArticle(articleId)} onReload={() => void loadArticles()} /></section><section className={`min-h-80 rounded-3xl border p-6 ${isDark ? "border-gray-800 bg-gray-900" : "border-gray-200 bg-white"}`}>{detailLoading && <div className="flex items-center gap-2 py-10 text-sm text-slate-500"><Loader2 className="h-4 w-4 animate-spin" /> Loading article…</div>}{detailError && <div className="rounded-2xl bg-red-50 p-4 text-sm text-red-800">{detailError}</div>}{actionError && <div className="mb-4 rounded-2xl bg-red-50 p-4 text-sm text-red-800">{actionError}</div>}{!detailLoading && !detailError && !editor && !detail && <div className={`flex min-h-64 flex-col items-center justify-center text-center ${isDark ? "text-gray-400" : "text-slate-500"}`}><BookOpen className="h-8 w-8" /><p className="mt-3 text-sm">Select an article to inspect its live content.</p></div>}{!detailLoading && !detailError && editor && canManage && <div className="space-y-5"><ArticleEditor articleId={selectedId} editor={editor} isSaving={saving} isPublishing={publishing} isPreviewing={previewing} isDark={isDark} onChange={(patch) => setEditor((current) => current ? { ...current, ...patch } : current)} onSave={() => void saveArticle()} onPublish={() => void publishArticle()} onPreview={() => void previewChunks()} /><ChunkPreviewList chunks={chunks} isDark={isDark} /></div>}{!detailLoading && !detailError && detail && !canManage && <ArticleReader article={detail} isDark={isDark} />}</section></div>}
    </div>
  );
}
