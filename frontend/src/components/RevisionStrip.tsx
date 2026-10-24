import { Plus, Check } from "lucide-react";
import { PrivateImage } from "./PrivateImage";
import type { Asset, Run } from "../types";

export function RevisionStrip({
  assets,
  runs,
  selectedId,
  onSelect,
  onUpload,
}: {
  assets: Asset[];
  runs: Run[];
  selectedId: string;
  onSelect: (id: string) => void;
  onUpload: () => void;
}) {
  return (
    <section className="revision-section">
      <div className="section-toolbar compact">
        <div className="section-title">
          <h3>Creative versions</h3>
          <span className="count-badge">{assets.length}</span>
        </div>
        <span className="small muted">Every idea has a place.</span>
      </div>
      <div className="revision-strip">
        {[...assets].reverse().map((asset, index) => (
          <button
            key={asset.id}
            className={`revision-card ${asset.id === selectedId ? "active" : ""}`}
            onClick={() => onSelect(asset.id)}
            aria-pressed={asset.id === selectedId}
          >
            <div className="revision-thumb">
              <PrivateImage
                path={`/assets/${asset.id}/image`}
                alt={asset.label}
              />
              {runs.some(
                (r) => r.asset_id === asset.id && r.status === "completed",
              ) && (
                <span className="revision-check">
                  <Check size={11} />
                </span>
              )}
            </div>
            <div>
              <span className="eyebrow">
                VERSION {String(index + 1).padStart(2, "0")}
              </span>
              <strong>{asset.label}</strong>
            </div>
          </button>
        ))}
        <button className="revision-add" onClick={onUpload}>
          <Plus size={22} strokeWidth={1.4} />
          <span>Add a revision</span>
        </button>
      </div>
    </section>
  );
}
