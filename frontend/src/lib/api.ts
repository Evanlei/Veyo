import { workspaceKey } from "./workspace";
import { IS_DEMO } from "./mode";
import { recordedRequest } from "./demo";
import type {
  Adjustment,
  Asset,
  Comparison,
  Health,
  Project,
  ProjectSummary,
  Run,
  Target,
} from "../types";

export const API_BASE = (import.meta.env.VITE_API_BASE_URL || "").replace(
  /\/$/,
  "",
);

export async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  if (IS_DEMO) {
    return recordedRequest<T>(path, options);
  }
  const headers = new Headers(options.headers);
  headers.set("X-Workspace-Key", workspaceKey());
  if (options.body && !(options.body instanceof FormData))
    headers.set("Content-Type", "application/json");
  let response: Response;
  try {
    response = await fetch(`${API_BASE}/api${path}`, { ...options, headers });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError")
      throw error;
    throw new Error("Cannot reach Veyo. Check your connection and try again.");
  }
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    const detail =
      typeof error.detail === "string"
        ? error.detail
        : "Check your input and try again.";
    throw new Error(detail);
  }
  if (
    response.headers.get("content-type")?.includes("application/json") &&
    !path.endsWith("report.json")
  )
    return response.json();
  return (await response.blob()) as T;
}

const json = (body: unknown) => JSON.stringify(body);
export const api = {
  health: () => request<Health>("/health"),
  projects: () => request<ProjectSummary[]>("/projects"),
  project: (id: string) => request<Project>(`/projects/${id}`),
  create: (file: File, name: string) => {
    const body = new FormData();
    body.set("image", file);
    body.set("name", name);
    return request<Project>("/projects", { method: "POST", body });
  },
  update: (id: string, patch: { name?: string; archived?: boolean }) =>
    request<Project>(`/projects/${id}`, { method: "PATCH", body: json(patch) }),
  upload: (id: string, file: File, label: string, parentId: string) => {
    const body = new FormData();
    body.set("image", file);
    body.set("label", label);
    body.set("parent_id", parentId);
    return request<Asset>(`/projects/${id}/assets`, { method: "POST", body });
  },
  targets: (id: string, targets: Target[]) =>
    request<Asset>(`/assets/${id}/targets`, {
      method: "PUT",
      body: json({ targets, confirmed: true }),
    }),
  analyze: (id: string) =>
    request<Run>(`/assets/${id}/analyze`, { method: "POST" }),
  adjust: (id: string, settings: Adjustment) =>
    request<Asset>(`/assets/${id}/adjust`, {
      method: "POST",
      body: json(settings),
    }),
  compare: (before: string, after: string) =>
    request<Comparison>("/comparisons", {
      method: "POST",
      body: json({ before_run_id: before, after_run_id: after }),
    }),
  sample: (id: string) =>
    request<Project>(`/samples/${id}`, { method: "POST" }),
};

export async function download(path: string, filename: string) {
  const blob = await request<Blob>(path);
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
