import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { SlidersHorizontal, ArrowUpRight } from "lucide-react";
import { api } from "../lib/api";
import { Modal } from "./Modal";
import { Button } from "./Button";
import { PrivateImage } from "./PrivateImage";
import type { Adjustment, Asset } from "../types";

const defaults: Adjustment = {
  label: "Controlled adjustment",
  brightness: 1,
  contrast: 1,
  saturation: 1,
  sharpness: 1,
  target_id: null,
};
export function AdjustmentDialog({
  asset,
  onClose,
  onCreated,
}: {
  asset: Asset;
  onClose: () => void;
  onCreated: (asset: Asset) => void;
}) {
  const [settings, setSettings] = useState(defaults);
  const update = (patch: Partial<Adjustment>) =>
    setSettings((previous) => ({ ...previous, ...patch }));
  const mutation = useMutation({
    mutationFn: () => api.adjust(asset.id, settings),
    onSuccess: onCreated,
  });
  return (
    <Modal title="Try one considered change." onClose={onClose}>
      <p className="muted modal-intro">
        Create a new version, then analyze it to see what changed. Your original
        stays intact.
      </p>
      <div
        className="adjustment-preview"
        style={
          !settings.target_id
            ? {
                filter: `brightness(${settings.brightness}) contrast(${settings.contrast}) saturate(${settings.saturation})`,
              }
            : {}
        }
      >
        <PrivateImage
          path={`/assets/${asset.id}/image`}
          alt="Adjustment reference"
        />
      </div>
      <p className="small muted">
        {settings.target_id
          ? "Reference image. The selected region is adjusted when you create the revision."
          : "Approximate preview. Saved output also applies sharpness and is the image that gets scored."}
      </p>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          mutation.mutate();
        }}
      >
        <label className="field-label" htmlFor="adjustment-label">
          Revision name
        </label>
        <input
          id="adjustment-label"
          value={settings.label}
          onChange={(e) => update({ label: e.target.value })}
          maxLength={100}
          required
        />
        <label className="field-label" htmlFor="adjustment-scope">
          Apply to
        </label>
        <select
          id="adjustment-scope"
          value={settings.target_id || ""}
          onChange={(e) => update({ target_id: e.target.value || null })}
        >
          <option value="">Whole creative</option>
          {asset.targets.map((t) => (
            <option key={t.id} value={t.id}>
              {t.label} only
            </option>
          ))}
        </select>
        <div className="adjustment-sliders">
          {(
            [
              { key: "brightness", label: "Brightness", min: 0.65, max: 1.35 },
              { key: "contrast", label: "Contrast", min: 0.65, max: 1.5 },
              { key: "saturation", label: "Saturation", min: 0, max: 1.5 },
              { key: "sharpness", label: "Sharpness", min: 0, max: 2 },
            ] as const
          ).map((control) => (
            <label key={control.key}>
              <span>
                {control.label}
                <output>{Math.round(settings[control.key] * 100)}%</output>
              </span>
              <input
                type="range"
                min={control.min}
                max={control.max}
                step="0.01"
                value={settings[control.key]}
                onChange={(e) =>
                  update({ [control.key]: Number(e.target.value) })
                }
              />
            </label>
          ))}
        </div>
        {mutation.error && (
          <p className="inline-error" role="alert">
            {mutation.error.message}
          </p>
        )}
        <div className="modal-actions">
          <Button
            type="button"
            icon={<SlidersHorizontal size={14} />}
            onClick={() => setSettings(defaults)}
          >
            Reset
          </Button>
          <Button
            variant="primary"
            type="submit"
            busy={mutation.isPending}
            disabled={!settings.label.trim()}
            icon={<ArrowUpRight size={15} />}
          >
            Create revision
          </Button>
        </div>
      </form>
    </Modal>
  );
}
