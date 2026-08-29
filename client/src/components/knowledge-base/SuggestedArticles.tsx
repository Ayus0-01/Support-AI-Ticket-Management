import { useEffect, useState } from "react";
import { BookOpen, ChevronRight, Loader2 } from "lucide-react";
import {
  searchKnowledgeBase,
  type KnowledgeSearchResult,
} from "../../services/knowledgeBaseService";

type SuggestedArticlesProps = {
  subject: string;
  description: string;
  affectedSystem?: string;
  category?: string;
  department?: string;
  isDark: boolean;
  onOpenArticle: (articleId: string) => void;
};

const getErrorMessage = (error: unknown) => {
  if (!error || typeof error !== "object") {
    return "Suggested articles are unavailable right now.";
  }

  const candidate = error as {
    message?: string;
    response?: { data?: { message?: string } };
  };

  return candidate.response?.data?.message || candidate.message || "Suggested articles are unavailable right now.";
};

export default function SuggestedArticles({
  subject,
  description,
  affectedSystem,
  category,
  department,
  isDark,
  onOpenArticle,
}: SuggestedArticlesProps) {
  const [results, setResults] = useState<KnowledgeSearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const query = [subject, description, affectedSystem]
      .map((part) => part?.trim())
      .filter(Boolean)
      .join(" ")
      .slice(0, 1800);

    if (query.length < 12) {
      setResults([]);
      setLoading(false);
      setError("");
      return undefined;
    }

    let active = true;
    const timer = window.setTimeout(() => {
      void (async () => {
        try {
          setLoading(true);
          setError("");
          const nextResults = await searchKnowledgeBase({
            query,
            top_k: 3,
            category: category && category !== "Not sure — let AI decide" ? category : undefined,
            department: department || undefined,
          });
          if (active) {
            setResults(nextResults);
          }
        } catch (searchError) {
          if (active) {
            setResults([]);
            setError(getErrorMessage(searchError));
          }
        } finally {
          if (active) {
            setLoading(false);
          }
        }
      })();
    }, 650);

    return () => {
      active = false;
      window.clearTimeout(timer);
    };
  }, [subject, description, affectedSystem, category, department]);

  return (
    <section className={`mt-6 rounded-2xl border p-4 ${isDark ? "border-gray-800 bg-gray-950" : "border-slate-200 bg-slate-50"}`}>
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <div className="rounded-lg bg-blue-600 p-1.5 text-white"><BookOpen className="h-4 w-4" /></div>
          <div>
            <p className={`text-sm font-bold ${isDark ? "text-white" : "text-slate-900"}`}>Suggested articles</p>
            <p className={`text-xs ${isDark ? "text-gray-400" : "text-slate-500"}`}>Live semantic matches; submitting your ticket is never delayed.</p>
          </div>
        </div>
        {loading && <Loader2 className="h-4 w-4 animate-spin text-blue-600" aria-label="Loading suggested articles" />}
      </div>
      {error && <p className="mt-3 rounded-xl bg-amber-50 p-3 text-xs text-amber-800">{error}</p>}
      {!loading && !error && results.length === 0 && <p className={`mt-4 text-sm ${isDark ? "text-gray-400" : "text-slate-500"}`}>Add a little more detail to see relevant published support articles.</p>}
      {results.length > 0 && <div className="mt-4 space-y-2">{results.map((result, index) => <button type="button" key={`${result.article_id}-${result.chunk_index ?? index}`} onClick={() => onOpenArticle(result.article_id)} className={`w-full rounded-xl border p-3 text-left transition ${isDark ? "border-gray-800 bg-gray-900 hover:border-gray-700" : "border-slate-200 bg-white hover:border-blue-300"}`}><div className="flex items-start justify-between gap-3"><div><p className={`text-sm font-semibold ${isDark ? "text-white" : "text-slate-900"}`}>{result.article_title || "Knowledge article"}</p><p className={`mt-1 text-xs ${isDark ? "text-gray-400" : "text-slate-500"}`}>{result.category || "Support knowledge"}{result.heading_path ? ` · ${result.heading_path}` : ""}</p></div><ChevronRight className="mt-0.5 h-4 w-4 shrink-0 text-blue-600" aria-hidden="true" /></div>{result.content && <p className={`mt-2 line-clamp-2 whitespace-pre-wrap text-xs leading-5 ${isDark ? "text-gray-300" : "text-slate-600"}`}>{result.content}</p>}<span className="mt-3 inline-block text-xs font-semibold text-blue-600">Read article</span></button>)}</div>}
    </section>
  );
}
