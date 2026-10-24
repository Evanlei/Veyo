import { ArrowUpRight, Info } from "lucide-react";
import { TARGET_COLORS } from "./CreativeCanvas";
import { percent, relative } from "../lib/format";
import type { Run } from "../types";

export function AttentionMetrics({
  run,
  selected,
  onSelect,
}: {
  run: Run;
  selected?: string;
  onSelect: (id: string) => void;
}) {
  if (!run.metrics) return null;
  const metrics = run.metrics;
  return (
    <div className="attention-metrics">
      <div className="rail-section-heading">
        <h2>Attention overview</h2>
        <span
          className="subtle-icon"
          title="Predicted fixation probability, summed over your targets"
        >
          <Info size={15} />
        </span>
      </div>
      <div className="primary-metric">
        <span className="metric-eyebrow">ON YOUR MARKED TARGETS</span>
        <strong>{percent(metrics.attention_share)}</strong>
        <p>of predicted visual attention</p>
        <div className="attention-meter">
          <span style={{ width: percent(metrics.attention_share) }} />
        </div>
        <small>
          Across {metrics.targets.length}{" "}
          {metrics.targets.length === 1 ? "target" : "targets"} · overlapping
          pixels counted once
        </small>
      </div>
      <div className="rail-section-heading">
        <h3>Attention by element</h3>
        <span className="column-label">SHARE</span>
      </div>
      <div className="metric-targets">
        {metrics.targets.map((target, index) => (
          <button
            key={target.id}
            className={`metric-target ${selected === target.id ? "active" : ""}`}
            onClick={() => onSelect(target.id)}
          >
            <span
              className="target-number"
              style={{ color: TARGET_COLORS[index] }}
            >
              {String(index + 1).padStart(2, "0")}
            </span>
            <div>
              <strong>{target.label}</strong>
              <small>
                {percent(target.area_share)} of image ·{" "}
                {relative(target.relative_attention)} average
              </small>
            </div>
            <b>{percent(target.attention_share)}</b>
            <ArrowUpRight size={13} />
          </button>
        ))}
      </div>
      <div className="metric-explainer">
        <Info size={15} />
        <p>
          <strong>Read the share alongside the size.</strong> A small target
          with a high share pulls more attention per pixel. Bigger isn’t
          automatically better.
        </p>
      </div>
    </div>
  );
}
