import { useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, ArrowRight, Columns2, Info, Layers2 } from "lucide-react";
import { api } from "../lib/api";
import { delta, percent, relative, timestamp } from "../lib/format";
import { CreativeCanvas } from "../components/CreativeCanvas";
import { ErrorState, Loading, EmptyState } from "../components/States";
import type { Project } from "../types";

export function Compare() {
  const { projectId = "" } = useParams();
  const query = useQuery({
    queryKey: ["project", projectId],
    queryFn: () => api.project(projectId),
  });
  if (query.isPending) return <Loading label="Gathering your versions…" />;
  if (query.isError)
    return (
      <ErrorState message={query.error.message} retry={() => query.refetch()} />
    );
  return <CompareContent project={query.data} />;
}

function CompareContent({ project }: { project: Project }) {
  const completed = project.runs.filter((r) => r.status === "completed");
  const [params, setParams] = useSearchParams();
  const beforeId = params.get("before") || completed.at(-1)?.id || "";
  const afterId = params.get("after") || completed[0]?.id || "";
  const [heatmaps, setHeatmaps] = useState(true);
  const [opacity, setOpacity] = useState(0.65);
  const query = useQuery({
    queryKey: ["comparison", beforeId, afterId],
    queryFn: () => api.compare(beforeId, afterId),
    enabled:
      completed.length >= 2 && !!beforeId && !!afterId && beforeId !== afterId,
  });
  const runLabel = (id: string) => {
    const run = completed.find((r) => r.id === id);
    if (!run) return "";
    const asset = project.assets.find((a) => a.id === run.asset_id);
    return `${asset?.label || "Creative"} · ${timestamp(run.created_at)}`;
  };
  return (
    <div className="page compare-page">
      <div className="breadcrumb">
        <Link to={`/creative/${project.id}`}>
          <ArrowLeft size={13} /> {project.name}
        </Link>
        <span>/</span>
        <span>Compare</span>
      </div>
      <div className="page-heading">
        <div>
          <div className="eyebrow">A LITTLE EVIDENCE, SIDE BY SIDE</div>
          <h1>What changed?</h1>
          <p className="page-description">
            A clearer comparison of corresponding creative elements.
          </p>
        </div>
        <Link
          className="button button-secondary"
          to={`/creative/${project.id}`}
        >
          <Layers2 size={15} />
          Back to creative
        </Link>
      </div>
      {completed.length < 2 ? (
        <div className="panel">
          <EmptyState
            icon={<Columns2 size={32} strokeWidth={1.3} />}
            title="Two analyses make a comparison."
          >
            <p>
              Analyze a revision, or a different set of targets, then come back
              here.
            </p>
            <Link
              className="button button-primary"
              to={`/creative/${project.id}`}
            >
              Open creative <ArrowRight size={15} />
            </Link>
          </EmptyState>
        </div>
      ) : (
        <>
          <div className="comparison-controls">
            <label>
              <span className="eyebrow">BEFORE</span>
              <select
                value={beforeId}
                onChange={(e) =>
                  setParams({ before: e.target.value, after: afterId })
                }
              >
                {completed.map((run) => (
                  <option key={run.id} value={run.id}>
                    {runLabel(run.id)}
                  </option>
                ))}
              </select>
            </label>
            <ArrowRight size={18} />
            <label>
              <span className="eyebrow">AFTER</span>
              <select
                value={afterId}
                onChange={(e) =>
                  setParams({ before: beforeId, after: e.target.value })
                }
              >
                {completed.map((run) => (
                  <option key={run.id} value={run.id}>
                    {runLabel(run.id)}
                  </option>
                ))}
              </select>
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={heatmaps}
                onChange={(e) => setHeatmaps(e.target.checked)}
              />
              Show heatmaps
            </label>
          </div>
          {beforeId === afterId ? (
            <div className="panel">
              <EmptyState
                icon={<Columns2 size={28} />}
                title="Choose two different analyses."
              >
                <p>Select another result to see the change.</p>
              </EmptyState>
            </div>
          ) : query.isPending ? (
            <Loading label="Comparing saved evidence…" />
          ) : query.isError ? (
            <ErrorState
              message={query.error.message}
              retry={() => query.refetch()}
            />
          ) : (
            query.data && (
              <>
                <div className="comparison-images">
                  {[
                    { title: "Before", run: query.data.before },
                    { title: "After", run: query.data.after },
                  ].map(({ title, run }) => {
                    const asset = project.assets.find(
                      (a) => a.id === run.asset_id,
                    )!;
                    return (
                      <section key={title} className="comparison-image-panel">
                        <div className="comparison-image-heading">
                          <span className="eyebrow">{title}</span>
                          <h3>{asset.label}</h3>
                          <span>
                            {asset.width} × {asset.height}
                          </span>
                        </div>
                        <CreativeCanvas
                          asset={asset}
                          targets={run.targets}
                          run={run}
                          mode={heatmaps ? "heatmap" : "original"}
                          opacity={opacity}
                        />
                      </section>
                    );
                  })}
                </div>
                {heatmaps && (
                  <div className="comparison-legend">
                    <div className="heatmap-legend">
                      <span>Less</span>
                      <span className="heatmap-gradient" />
                      <span>More predicted attention</span>
                    </div>
                    <label className="opacity-control">
                      Overlay
                      <input
                        type="range"
                        aria-label="Comparison heatmap opacity"
                        min="0"
                        max="1"
                        step="0.05"
                        value={opacity}
                        onChange={(e) => setOpacity(Number(e.target.value))}
                      />
                    </label>
                  </div>
                )}
                <section className="comparison-evidence">
                  <div className="section-toolbar">
                    <div>
                      <div className="eyebrow">
                        THE DIFFERENCE IN THE DETAILS
                      </div>
                      <h2>Attention on what matters.</h2>
                    </div>
                    <p className="muted small">
                      Changes shown in percentage points.
                    </p>
                  </div>
                  <div className="table-scroll">
                    <table>
                      <thead>
                        <tr>
                          <th>Element</th>
                          <th>Before share</th>
                          <th>After share</th>
                          <th>Change</th>
                          <th>Area, before → after</th>
                          <th>Relative attention</th>
                        </tr>
                      </thead>
                      <tbody>
                        {query.data.targets.map((target, index) => (
                          <tr key={`${target.role}:${target.label}`}>
                            <td>
                              <span className="target-number">
                                {String(index + 1).padStart(2, "0")}
                              </span>
                              <strong>{target.label}</strong>
                              <small>{target.role}</small>
                            </td>
                            <td>{percent(target.before.attention_share)}</td>
                            <td>{percent(target.after.attention_share)}</td>
                            <td>
                              <span
                                className={`delta-badge ${target.delta_pp > 0.1 ? "positive" : target.delta_pp < -0.1 ? "negative" : ""}`}
                              >
                                {delta(target.delta_pp)}
                              </span>
                            </td>
                            <td>
                              {percent(target.before.area_share)} →{" "}
                              {percent(target.after.area_share)}
                            </td>
                            <td>
                              {relative(target.before.relative_attention)} →{" "}
                              {relative(target.after.relative_attention)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  <p className="comparison-note">
                    <Info size={16} />
                    {query.data.note}
                    {!query.data.same_dimensions &&
                      " The creatives have different dimensions; assess composition changes as well."}
                  </p>
                </section>
                <div className="comparison-bottom-note">
                  <strong>A higher share is a signal to investigate.</strong>
                  <p>
                    Review the whole creative, its message, and its brand fit. A
                    model score alone doesn’t establish that a revision is
                    better.
                  </p>
                </div>
              </>
            )
          )}
        </>
      )}
    </div>
  );
}
