import { useState } from "react";
import { Download, FileJson, Image, Package } from "lucide-react";
import { Modal } from "./Modal";
import { Button } from "./Button";
import { download } from "../lib/api";
import type { Asset, Run } from "../types";

export function ExportDialog({
  projectId,
  asset,
  run,
  onClose,
}: {
  projectId: string;
  asset: Asset;
  run?: Run;
  onClose: () => void;
}) {
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const get = async (path: string, filename: string) => {
    setBusy(path);
    setError("");
    try {
      await download(path, filename);
    } catch (error) {
      setError((error as Error).message);
    } finally {
      setBusy("");
    }
  };
  const items = [
    {
      path: `/assets/${asset.id}/image`,
      filename: "veyo-creative.png",
      title: "Creative image",
      description: "Canonical PNG, ready for your design workflow.",
      icon: <Image size={19} />,
    },
    ...(run
      ? [
          {
            path: `/runs/${run.id}/overlay.png`,
            filename: "veyo-heatmap.png",
            title: "Heatmap overlay",
            description: "The creative with its predicted attention overlay.",
            icon: <Image size={19} />,
          },
          {
            path: `/runs/${run.id}/report.json`,
            filename: "veyo-analysis.json",
            title: "Analysis report",
            description: "Scores, target geometry, and model provenance.",
            icon: <FileJson size={19} />,
          },
        ]
      : []),
    {
      path: `/projects/${projectId}/export`,
      filename: "veyo-project.zip",
      title: "Complete project",
      description: "Every revision and its evidence in one portable ZIP.",
      icon: <Package size={19} />,
    },
  ];
  return (
    <Modal title="Take your findings with you." onClose={onClose}>
      <p className="muted modal-intro">
        Share the evidence alongside the creative.
      </p>
      <div className="export-list">
        {items.map((item) => (
          <div key={item.path} className="export-item">
            {item.icon}
            <div>
              <strong>{item.title}</strong>
              <p>{item.description}</p>
            </div>
            <Button
              disabled={!!busy}
              busy={busy === item.path}
              icon={<Download size={16} />}
              aria-label={`Download ${item.title}`}
              onClick={() => get(item.path, item.filename)}
            />
          </div>
        ))}
      </div>
      {error && (
        <p className="inline-error" role="alert">
          {error}
        </p>
      )}
    </Modal>
  );
}
