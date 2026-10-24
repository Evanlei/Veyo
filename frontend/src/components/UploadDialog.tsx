import { useEffect, useRef, useState } from "react";
import { Upload, ImagePlus, ArrowUpRight } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import { Modal } from "./Modal";
import { Button } from "./Button";
import { api } from "../lib/api";
import { titleFromFile } from "../lib/format";
import type { Asset, Project } from "../types";

export function UploadDialog({
  onClose,
  onCreated,
  projectId,
  parentId,
}: {
  onClose: () => void;
  onCreated: (value: Project | Asset) => void;
  projectId?: string;
  parentId?: string;
}) {
  const [file, setFile] = useState<File>();
  const [name, setName] = useState("");
  const [preview, setPreview] = useState("");
  const [error, setError] = useState("");
  const [dragging, setDragging] = useState(false);
  const input = useRef<HTMLInputElement>(null);
  useEffect(() => {
    if (!file) return;
    const url = URL.createObjectURL(file);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);
  const choose = (next?: File) => {
    if (!next) return;
    if (
      !["image/jpeg", "image/png"].includes(next.type) ||
      next.size > 12 * 1024 * 1024
    ) {
      setError("Choose a PNG or JPEG smaller than 12 MB.");
      return;
    }
    setFile(next);
    setName(titleFromFile(next.name));
    setError("");
  };
  const mutation = useMutation({
    mutationFn: () => {
      if (!file) throw new Error("Choose a creative first.");
      return projectId
        ? api.upload(projectId, file, name, parentId!)
        : api.create(file, name);
    },
    onSuccess: onCreated,
  });
  return (
    <Modal
      title={projectId ? "Add a revision" : "A fresh perspective starts here."}
      onClose={onClose}
    >
      <p className="muted modal-intro">
        {projectId
          ? "Upload your next version, then mark its corresponding targets before comparing."
          : "Bring a static creative. Find out where predicted attention goes."}
      </p>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          mutation.mutate();
        }}
      >
        <input
          ref={input}
          type="file"
          accept="image/png,image/jpeg"
          className="sr-only"
          aria-label="Creative image file"
          onChange={(e) => choose(e.target.files?.[0])}
        />
        <button
          type="button"
          className={`upload-zone ${dragging ? "dragging" : ""} ${file ? "has-file" : ""}`}
          onClick={() => input.current?.click()}
          onDragOver={(e) => {
            e.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragging(false);
            choose(e.dataTransfer.files[0]);
          }}
        >
          {preview ? (
            <img src={preview} alt="Selected creative preview" />
          ) : (
            <>
              <span className="upload-icon">
                <ImagePlus size={30} strokeWidth={1.4} />
              </span>
              <strong>Drop your creative here</strong>
              <span>or click to browse files</span>
              <small>PNG or JPEG · Up to 12 MB</small>
            </>
          )}
          {file && (
            <span className="replace-file">
              <Upload size={14} /> Choose another image
            </span>
          )}
        </button>
        <label className="field-label" htmlFor="creative-name">
          {projectId ? "Revision name" : "Creative name"}
        </label>
        <input
          id="creative-name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          maxLength={100}
          placeholder="e.g. Summer skincare campaign"
          required
          disabled={mutation.isPending}
        />
        {(error || mutation.error) && (
          <p className="inline-error" role="alert">
            {error || mutation.error?.message}
          </p>
        )}
        <div className="modal-actions">
          <Button type="button" onClick={onClose}>
            Cancel
          </Button>
          <Button
            type="submit"
            variant="primary"
            busy={mutation.isPending}
            disabled={!file || !name.trim()}
            icon={<ArrowUpRight size={16} />}
          >
            {projectId ? "Add revision" : "Open creative"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
