import { ArrowUpRight, Focus, ScanEye } from "lucide-react";
import { percent, relative } from "../lib/format";
import type { Run } from "../types";

export function Insights({
  run,
  showCompeting,
  onToggleCompeting,
}: {
  run: Run;
  showCompeting: boolean;
  onToggleCompeting: () => void;
}) {
  const targets = [...(run.metrics?.targets || [])].sort(
    (a, b) => b.priority - a.priority || b.attention_share - a.attention_share,
  );
  const primary = targets[0];
  return (
    <section className="insights-panel">
      <div className="rail-section-heading">
        <h3>
          <ScanEye size={16} /> A closer look
        </h3>
      </div>
      {primary && (
        <p>
          <strong>{primary.label}</strong> draws{" "}
          {percent(primary.attention_share)} of predicted attention from{" "}
          {percent(primary.area_share)} of the image. That’s{" "}
          <strong>{relative(primary.relative_attention)}</strong> the image
          average per pixel.
        </p>
      )}
      {!!run.competing_regions?.length && (
        <>
          <div className="insight-divider" />
          <div className="rail-section-heading">
            <h4>Outside your targets</h4>
            <button
              className={`icon-button ${showCompeting ? "active" : ""}`}
              aria-label="Highlight competing regions"
              aria-pressed={showCompeting}
              onClick={onToggleCompeting}
            >
              <Focus size={16} />
            </button>
          </div>
          <p className="small muted">
            These regions may compete for attention. Review their purpose before
            changing them.
          </p>
          <ol className="competing-list">
            {run.competing_regions.map((region, index) => (
              <li key={index}>
                <span>{index + 1}</span>
                {region.label}
                <strong>{percent(region.attention_share)}</strong>
                <ArrowUpRight size={12} />
              </li>
            ))}
          </ol>
        </>
      )}
      <p className="model-note">
        Spatial predictions don’t establish the order people look, or how the ad
        will perform.
      </p>
    </section>
  );
}
