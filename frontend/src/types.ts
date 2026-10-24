export type Box = [number, number, number, number];
export type Role = "product" | "headline" | "logo" | "cta" | "other";
export interface Target {
  id: string;
  label: string;
  role: Role;
  box: Box;
  priority: number;
}
export interface TargetMetric extends Target {
  attention_share: number;
  area_share: number;
  relative_attention: number;
}
export interface Asset {
  id: string;
  project_id: string;
  label: string;
  created_at: string;
  width: number;
  height: number;
  sha256: string;
  targets: Target[];
  confirmed: boolean;
  parent_id: string | null;
  provenance: {
    kind: string;
    resized?: boolean;
    source_width?: number;
    source_height?: number;
    changed_pixel_share?: number;
    settings?: Record<string, unknown>;
  };
}
export interface Run {
  id: string;
  project_id: string;
  asset_id: string;
  created_at: string;
  status: "running" | "completed" | "failed";
  width: number;
  height: number;
  targets: Target[];
  error?: string;
  cached?: boolean;
  seconds?: number;
  model?: {
    model: string;
    source_commit: string;
    centerbias: string;
    device: string;
    package_version: string;
  };
  metrics?: {
    targets: TargetMetric[];
    attention_share: number;
    area_share: number;
    overlap_note: string;
  };
  competing_regions?: { box: Box; attention_share: number; label: string }[];
}
export interface Project {
  id: string;
  name: string;
  archived: boolean;
  created_at: string;
  assets: Asset[];
  runs: Run[];
}
export interface ProjectSummary extends Omit<Project, "assets" | "runs"> {
  cover_asset: Asset | null;
  asset_count: number;
  analysis_count: number;
  latest_run: Run | null;
}
export interface Health {
  status: string;
  model: string;
  loaded: boolean;
  busy: boolean;
  fallback: boolean;
  storage: string;
}
export interface Adjustment {
  label: string;
  brightness: number;
  contrast: number;
  saturation: number;
  sharpness: number;
  target_id: string | null;
}
export interface Comparison {
  before: Run;
  after: Run;
  same_dimensions: boolean;
  note: string;
  targets: {
    label: string;
    role: Role;
    before: TargetMetric;
    after: TargetMetric;
    delta_pp: number;
    relative_delta: number;
  }[];
}
