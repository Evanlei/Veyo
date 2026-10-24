import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Copy,
  Download,
  KeyRound,
  ArrowRight,
  ShieldCheck,
} from "lucide-react";
import { api } from "../lib/api";
import { workspaceKey, importWorkspace } from "../lib/workspace";
import { Button } from "../components/Button";
import { useToast } from "../components/Toast";

export function Settings() {
  const toast = useToast();
  const [revealed, setRevealed] = useState(false);
  const [key, setKey] = useState("");
  const [error, setError] = useState("");
  const health = useQuery({ queryKey: ["health"], queryFn: api.health });
  const backup = () => {
    const url = URL.createObjectURL(
      new Blob([workspaceKey() + "\n"], { type: "text/plain" }),
    );
    const link = document.createElement("a");
    link.href = url;
    link.download = "veyo-workspace-key.txt";
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    toast("Workspace key downloaded. Keep it somewhere private.");
  };
  return (
    <div className="page settings-page">
      <div className="eyebrow">YOUR SPACE, YOUR WORK</div>
      <h1>Workspace settings.</h1>
      <p className="page-description">
        Keep your creative library within reach.
      </p>
      <div className="settings-grid">
        <section className="settings-card">
          <div className="settings-icon">
            <KeyRound size={23} />
          </div>
          <h2>Your workspace key</h2>
          <p>
            This browser holds a private key that opens your saved creative
            library. Back it up to restore your work on another device.
          </p>
          <div className="key-box">
            <code>
              {revealed
                ? workspaceKey()
                : "•••• •••• •••• •••• •••• •••• •••• ••••"}
            </code>
            <button
              className="text-link"
              onClick={() => setRevealed(!revealed)}
            >
              {revealed ? "Hide" : "Reveal"}
            </button>
          </div>
          <div className="settings-actions">
            <Button icon={<Download size={15} />} onClick={backup}>
              Download key
            </Button>
            <Button
              icon={<Copy size={15} />}
              onClick={async () => {
                try {
                  await navigator.clipboard.writeText(workspaceKey());
                  toast("Workspace key copied.");
                } catch {
                  toast(
                    "Clipboard unavailable. Download your key instead.",
                    true,
                  );
                }
              }}
            >
              Copy key
            </Button>
          </div>
          <p className="small privacy-note">
            <ShieldCheck size={15} />
            Anyone with this key can access this workspace. Keep it private.
            Clearing browser storage without a backup can lose access to your
            work.
          </p>
        </section>
        <section className="settings-card">
          <h2>Open another workspace</h2>
          <p>
            Paste a backed-up workspace key. Your current workspace remains
            available through its own key.
          </p>
          <form
            onSubmit={(event) => {
              event.preventDefault();
              try {
                importWorkspace(key);
                location.assign("/");
              } catch (error) {
                setError((error as Error).message);
              }
            }}
          >
            <label className="field-label" htmlFor="restore-key">
              Workspace key
            </label>
            <input
              id="restore-key"
              autoComplete="off"
              spellCheck={false}
              value={key}
              onChange={(event) => setKey(event.target.value)}
              placeholder="64-character private key"
              required
              minLength={64}
              maxLength={64}
            />
            {error && (
              <p className="inline-error" role="alert">
                {error}
              </p>
            )}
            <Button
              className="restore-button"
              variant="primary"
              type="submit"
              icon={<ArrowRight size={15} />}
            >
              Open workspace
            </Button>
          </form>
        </section>
      </div>
      <section className="service-card">
        <h2>Analysis service</h2>
        <dl>
          <div>
            <dt>Model</dt>
            <dd>DeepGaze IIE</dd>
          </div>
          <div>
            <dt>Connection</dt>
            <dd>
              {health.isError
                ? "Unavailable"
                : health.isPending
                  ? "Checking…"
                  : "Connected"}
            </dd>
          </div>
          <div>
            <dt>Inference</dt>
            <dd>{health.data?.loaded ? "Ready" : "Loads on first analysis"}</dd>
          </div>
          <div>
            <dt>Storage</dt>
            <dd>
              {health.data?.storage === "cloud"
                ? "Durable cloud files"
                : "Local files"}
            </dd>
          </div>
        </dl>
      </section>
    </div>
  );
}
