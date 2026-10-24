import { useQuery } from "@tanstack/react-query";
import { ArrowUpRight, CirclePlay } from "lucide-react";
import { loadRecording } from "../lib/demo";
import { LOCAL_GUIDE } from "../lib/mode";
import { ErrorState, Loading } from "./States";

export function DemoNotice() {
  return (
    <div className="demo-notice" role="note">
      <span>
        <CirclePlay size={16} />
        <strong>Recorded demo</strong>
      </span>
      <p>
        Explore real saved analyses. Uploads and fresh predictions run in the
        local app.
      </p>
      <a href={LOCAL_GUIDE} target="_blank" rel="noreferrer">
        Run locally <ArrowUpRight size={14} />
      </a>
    </div>
  );
}

export function DemoDetails() {
  const query = useQuery({ queryKey: ["recording"], queryFn: loadRecording });
  if (query.isPending)
    return <Loading label="Opening the recording details…" />;
  if (query.isError)
    return (
      <ErrorState message={query.error.message} retry={() => query.refetch()} />
    );
  return (
    <div className="page settings-page">
      <div className="eyebrow">A CLOSER LOOK AT THIS DEMO</div>
      <h1>Real predictions. Recorded examples.</h1>
      <p className="page-description">
        Three fictional creatives, each with an original and a controlled
        revision. Every heatmap and score was computed with DeepGaze IIE before
        publication.
      </p>
      <section className="settings-card">
        <h2>What you can explore</h2>
        <p>
          Switch between creatives and versions, inspect targets and competing
          regions, adjust heatmap opacity, compare saved results, and download
          the evidence.
        </p>
        <p>
          This public site runs without an analysis server. It does not accept
          uploads, create revisions, change saved annotations, or run new
          predictions. There are no private workspace keys in this demo.
        </p>
        <a
          className="button button-primary"
          href={LOCAL_GUIDE}
          target="_blank"
          rel="noreferrer"
        >
          Analyze your own creative locally <ArrowUpRight size={16} />
        </a>
      </section>
      <section className="service-card">
        <h2>Recording provenance</h2>
        <dl>
          <div>
            <dt>Model</dt>
            <dd>{query.data.model.model}</dd>
          </div>
          <div>
            <dt>Computed on</dt>
            <dd>CPU · uniform spatial prior</dd>
          </div>
          <div>
            <dt>Recorded</dt>
            <dd>{new Date(query.data.recorded_at).toLocaleDateString()}</dd>
          </div>
          <div>
            <dt>Source version</dt>
            <dd>{query.data.model.source_commit.slice(0, 8)}</dd>
          </div>
        </dl>
        <p className="small muted">
          The same model and metrics power the complete local application. These
          are spatial predictions, not measured viewer behavior or advertising
          performance.
        </p>
        <a
          className="text-link"
          href="/demo/manifest.json"
          target="_blank"
          rel="noreferrer"
        >
          View recording data <ArrowUpRight size={14} />
        </a>
      </section>
    </div>
  );
}
