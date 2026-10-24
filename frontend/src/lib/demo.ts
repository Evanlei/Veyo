import type { Comparison, Project, ProjectSummary, Run } from "../types";

export interface Recording {
  version: number;
  mode: "recorded";
  recorded_at: string;
  model: NonNullable<Run["model"]>;
  projects: Project[];
  samples: Record<string, string>;
  files: Record<string, { url: string; sha256: string; bytes: number }>;
}

let recording: Promise<Recording> | undefined;
export function loadRecording() {
  if (!recording) {
    recording = fetch("/demo/manifest.json")
      .then(async (response) => {
        if (!response.ok)
          throw new Error(
            "The recorded examples could not be loaded. Refresh to try again.",
          );
        const data: Recording = await response.json();
        if (
          data.version !== 1 ||
          data.mode !== "recorded" ||
          !data.projects.length
        )
          throw new Error("This recording format is not supported.");
        return data;
      })
      .catch((error) => {
        recording = undefined;
        throw error;
      });
  }
  return recording;
}

export function compareRecordedRuns(before: Run, after: Run): Comparison {
  if (
    before.project_id !== after.project_id ||
    before.status !== "completed" ||
    after.status !== "completed"
  )
    throw new Error("Choose two completed recordings from the same creative.");
  if (
    !before.metrics ||
    !after.metrics ||
    JSON.stringify(before.model) !== JSON.stringify(after.model)
  )
    throw new Error(
      "These recordings cannot be compared with the same model settings.",
    );
  const targets = before.metrics.targets.flatMap((target) => {
    const match = after.metrics!.targets.find(
      (other) =>
        other.role === target.role &&
        other.label.toLowerCase() === target.label.toLowerCase(),
    );
    return match
      ? [
          {
            label: target.label,
            role: target.role,
            before: target,
            after: match,
            delta_pp: (match.attention_share - target.attention_share) * 100,
            relative_delta:
              match.relative_attention - target.relative_attention,
          },
        ]
      : [];
  });
  if (!targets.length)
    throw new Error("These recordings have no corresponding targets.");
  return {
    before,
    after,
    targets,
    same_dimensions:
      before.width === after.width && before.height === after.height,
    note: "Compared from saved DeepGaze IIE results. No new inference was run.",
  };
}

export async function recordedRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const method = (options.method || "GET").toUpperCase();
  // Block live operations even if a caller bypasses the read-only interface.
  if (
    method !== "GET" &&
    !(
      method === "POST" &&
      (path === "/comparisons" || /^\/samples\/[a-z]+$/.test(path))
    )
  )
    throw new Error(
      "This public demo shows recorded examples. Run Veyo locally to upload, edit targets, or analyze your own creative.",
    );
  const data = await loadRecording();
  if (options.signal?.aborted) throw new DOMException("Aborted", "AbortError");
  let value: unknown;
  if (path === "/health" && method === "GET") {
    value = {
      status: "ok",
      model: "DeepGaze IIE",
      loaded: false,
      busy: false,
      fallback: false,
      storage: "recorded",
    };
  } else if (path === "/projects" && method === "GET") {
    value = data.projects.map((project): ProjectSummary => {
      const { assets, runs, ...metadata } = project;
      return {
        ...metadata,
        cover_asset: assets.at(-1) || null,
        asset_count: assets.length,
        analysis_count: runs.length,
        latest_run: runs[0] || null,
      };
    });
  } else if (path.startsWith("/samples/") && method === "POST") {
    value = data.projects.find(
      (project) => project.id === data.samples[path.split("/")[2]],
    );
  } else if (/^\/projects\/[^/]+$/.test(path) && method === "GET") {
    value = data.projects.find((project) => project.id === path.split("/")[2]);
  } else if (path === "/comparisons" && method === "POST") {
    const body = JSON.parse(String(options.body));
    const runs = data.projects.flatMap((project) => project.runs);
    const before = runs.find((run) => run.id === body.before_run_id);
    const after = runs.find((run) => run.id === body.after_run_id);
    if (before && after) value = compareRecordedRuns(before, after);
  } else if (method === "GET" && Object.hasOwn(data.files, path)) {
    const file = data.files[path];
    if (!file.url.startsWith("/demo/"))
      throw new Error("Invalid recording artifact.");
    const response = await fetch(file.url, { signal: options.signal });
    if (!response.ok)
      throw new Error(
        "This recorded download is unavailable. Refresh and try again.",
      );
    return (await response.blob()) as T;
  }
  if (value === undefined)
    throw new Error("This item is not part of the public recording.");
  return structuredClone(value) as T;
}
