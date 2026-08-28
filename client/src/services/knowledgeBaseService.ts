import api from "../api";

export type KnowledgeArticleStatus = "DRAFT" | "PUBLISHED" | "ARCHIVED" | string;

export type KnowledgeArticle = {
  id: string;
  slug: string;
  title: string;
  category: string;
  sub_category: string;
  tags: string[];
  status: KnowledgeArticleStatus;
  version: number;
  source_system: "MANUAL" | "CONFLUENCE" | "SHAREPOINT" | "UPLOAD" | string;
  is_internal_only: boolean;
  chunk_count: number;
  indexed_version: number | null;
  embedding_model?: string | null;
  index_error?: string | null;
  updated_at: string;
  created_at: string;
};

export type KnowledgeArticleDetail = KnowledgeArticle & {
  content: string;
  source_url?: string | null;
  visible_to_departments?: string[];
  content_hash?: string;
  last_indexed_at?: string | null;
  author_id?: string | null;
  author_name?: string;
  reviewed_by_id?: string | null;
  source_updated_at?: string | null;
};

type KnowledgeArticleTransport = KnowledgeArticleDetail & {
  _id?: string;
};

export type KnowledgeArticleInput = {
  title: string;
  slug: string;
  category: string;
  sub_category: string;
  tags: string[];
  content: string;
  source_system: "MANUAL" | "CONFLUENCE" | "SHAREPOINT" | "UPLOAD";
  source_url?: string | null;
  visible_to_departments: string[];
  is_internal_only: boolean;
};

export type KnowledgeArticleUpdate = Partial<KnowledgeArticleInput> & {
  change_note?: string;
};

export type ChunkPreview = {
  index: number;
  heading_path: string;
  token_count: number;
  content: string;
};

export type KnowledgeSearchOptions = {
  query: string;
  limit?: number;
  top_k?: number;
  category?: string;
  department?: string;
  include_internal?: boolean;
};

export type KnowledgeSearchResult = {
  article_id: string;
  article_title?: string;
  article_slug?: string;
  article_status?: string;
  category?: string;
  sub_category?: string;
  content?: string;
  chunk_index?: number;
  heading_path?: string;
  article_updated_at?: string;
  rerank_score?: number;
};

export type IngestionProgress = {
  total_documents: number;
  processed: number;
  articles_created: number;
  articles_updated: number;
  failed: number;
  chunks_created: number;
  chunks_embedded: number;
};

export type IngestionError = {
  document?: string;
  stage?: string;
  message?: string;
};

export type IngestionResult = {
  path?: string;
  article_id?: string;
  title?: string;
  version?: number;
  indexed_version?: number;
  chunk_count?: number;
  created?: boolean;
  status?: string;
};

export type IngestionJob = {
  job_id: string;
  status: string;
  progress: IngestionProgress;
  errors: IngestionError[];
  results?: IngestionResult[];
  finished_at?: string;
  duration_ms?: number;
};

export type KnowledgeGap = {
  query?: string;
  category?: string;
  department?: string;
  occurrence_count?: number;
  last_seen_at?: string;
  created_at?: string;
  [key: string]: unknown;
};

const messageFromResponse = (data: unknown, fallback: string) => {
  if (data && typeof data === "object" && "message" in data) {
    const message = (data as { message?: unknown }).message;
    if (typeof message === "string") {
      return message;
    }
  }

  return fallback;
};

const normalizeArticle = (article: KnowledgeArticleTransport): KnowledgeArticleDetail => ({
  ...article,
  id: article.id ?? article._id ?? "",
});

export const getKnowledgeArticles = async (includeArchived = false): Promise<KnowledgeArticle[]> => {
  const response = await api.get("/api/knowledge/articles/", {
    params: includeArchived ? { include_archived: "true" } : undefined,
  });
  const articles = response.data?.articles;

  if (!Array.isArray(articles)) {
    throw new Error("Knowledge Base response did not contain an article list.");
  }

  return articles.map((article) => normalizeArticle(article as KnowledgeArticleTransport));
};

export const getKnowledgeArticle = async (articleId: string): Promise<KnowledgeArticleDetail> => {
  const response = await api.get(`/api/knowledge/articles/${articleId}/`);
  const article = response.data?.article;

  if (!article) {
    throw new Error(messageFromResponse(response.data, "Knowledge article was not found."));
  }

  return normalizeArticle(article as KnowledgeArticleTransport);
};

export const createKnowledgeArticle = async (article: KnowledgeArticleInput): Promise<KnowledgeArticleDetail> => {
  const response = await api.post("/api/knowledge/articles/", article);
  const created = response.data?.article;

  if (!created) {
    throw new Error(messageFromResponse(response.data, "Knowledge article could not be created."));
  }

  return normalizeArticle(created as KnowledgeArticleTransport);
};

export const updateKnowledgeArticle = async (
  articleId: string,
  article: KnowledgeArticleUpdate,
): Promise<KnowledgeArticleDetail> => {
  const response = await api.put(`/api/knowledge/articles/${articleId}/`, article);
  const updated = response.data?.article;

  if (!updated) {
    throw new Error(messageFromResponse(response.data, "Knowledge article could not be updated."));
  }

  return normalizeArticle(updated as KnowledgeArticleTransport);
};

export const publishKnowledgeArticle = async (
  articleId: string,
  changeNote?: string,
): Promise<KnowledgeArticleDetail> => {
  const response = await api.post(`/api/knowledge/articles/${articleId}/publish/`, {
    change_note: changeNote || "Published from Knowledge Base",
  });
  const article = response.data?.article;

  if (!article) {
    throw new Error(messageFromResponse(response.data, "Knowledge article could not be published."));
  }

  return normalizeArticle(article as KnowledgeArticleTransport);
};

export const previewKnowledgeArticleChunks = async (
  articleId: string,
  content: string,
  title?: string,
): Promise<ChunkPreview[]> => {
  const response = await api.post(`/api/knowledge/articles/${articleId}/preview-chunks/`, {
    title,
    content,
  });
  const chunks = response.data?.chunks;

  if (!Array.isArray(chunks)) {
    throw new Error(messageFromResponse(response.data, "Chunk preview could not be generated."));
  }

  return chunks;
};

export const searchKnowledgeBase = async (
  options: KnowledgeSearchOptions,
): Promise<KnowledgeSearchResult[]> => {
  const response = await api.post("/api/knowledge/search/", options);
  const results = response.data?.results;

  if (!Array.isArray(results)) {
    throw new Error(messageFromResponse(response.data, "Knowledge Base search did not return results."));
  }

  return results;
};

export const uploadKnowledgeDocuments = async (
  files: File[],
  sourceMetadata: Record<string, unknown> = {},
): Promise<IngestionJob> => {
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));
  formData.append("job_type", "BULK_UPLOAD");
  formData.append("source_metadata", JSON.stringify(sourceMetadata));

  const response = await api.post("/api/knowledge/ingest-upload/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  if (!response.data?.job_id) {
    throw new Error(messageFromResponse(response.data, "Documents could not be ingested."));
  }

  return response.data;
};

export const getIngestionStatus = async (jobId: string): Promise<IngestionJob> => {
  const response = await api.get(`/api/knowledge/ingest/${jobId}/`);
  const job = response.data?.job;

  if (!job) {
    throw new Error(messageFromResponse(response.data, "Ingestion job was not found."));
  }

  return {
    ...job,
    job_id: String(job.job_id ?? job._id ?? jobId),
  };
};

export const getKnowledgeGaps = async (): Promise<KnowledgeGap[]> => {
  const response = await api.get("/api/knowledge/gaps/");
  const gaps = response.data?.gaps;

  if (!Array.isArray(gaps)) {
    throw new Error(messageFromResponse(response.data, "Knowledge Base gaps could not be loaded."));
  }

  return gaps;
};
