import { afterEach, describe, expect, it, vi } from "vitest";
import recordingData from "../../public/demo/manifest.json";
import { compareRecordedRuns, recordedRequest } from "./demo";
import type { Project, ProjectSummary } from "../types";

// JSON imports infer number[] rather than the validated four-coordinate tuple.
const projects = recordingData.projects as unknown as Project[];
afterEach(() => vi.unstubAllGlobals());

describe("truthful recorded demo", () => {
  it("blocks uploads, annotation changes, live inference, and arbitrary mutations before making any request", async () => {
    const fetch = vi.fn();
    vi.stubGlobal("fetch", fetch);
    for (const [path, method] of [
      ["/projects", "POST"],
      ["/assets/x/targets", "PUT"],
      ["/assets/x/analyze", "POST"],
      ["/assets/x/adjust", "POST"],
      ["/projects/x", "PATCH"],
    ]) {
      await expect(recordedRequest(path, { method })).rejects.toThrow(
        "Run Veyo locally",
      );
    }
    expect(fetch).not.toHaveBeenCalled();
  });

  it("loads public examples without workspace credentials, returns independent snapshots, and rejects unknown items", async () => {
    const fetch = vi.fn(
      async () =>
        new Response(JSON.stringify(recordingData), {
          headers: { "Content-Type": "application/json" },
        }),
    );
    vi.stubGlobal("fetch", fetch);
    const list = await recordedRequest<ProjectSummary[]>("/projects");
    expect(list).toHaveLength(3);
    expect(
      list.every((p) => p.asset_count === 2 && p.analysis_count === 2),
    ).toBe(true);
    expect(fetch).toHaveBeenCalledWith("/demo/manifest.json");
    list[0].name = "changed locally";
    const second = await recordedRequest<ProjectSummary[]>("/projects");
    expect(second[0].name).not.toBe("changed locally");
    const sample = await recordedRequest<Project>("/samples/forma", {
      method: "POST",
    });
    expect(sample.id).toBe(recordingData.samples.forma);
    await expect(recordedRequest("/projects/missing")).rejects.toThrow(
      "not part of the public recording",
    );
    expect(fetch).toHaveBeenCalledTimes(1);
  });

  it("preserves genuine gains and losses, including reversed comparisons", () => {
    const forma = projects.find((p) => p.id === recordingData.samples.forma)!;
    const original = forma.assets.find((a) => !a.parent_id)!;
    const before = forma.runs.find((r) => r.asset_id === original.id)!;
    const after = forma.runs.find((r) => r.asset_id !== original.id)!;
    const forward = compareRecordedRuns(before, after);
    expect(
      forward.targets.find((t) => t.role === "product")!.delta_pp,
    ).toBeCloseTo(0.42417, 4);
    expect(
      forward.targets.find((t) => t.role === "logo")!.delta_pp,
    ).toBeCloseTo(-0.17612, 4);
    const reverse = compareRecordedRuns(after, before);
    forward.targets.forEach((target, i) =>
      expect(reverse.targets[i].delta_pp).toBeCloseTo(-target.delta_pp, 10),
    );
    const fieldwork = projects.find(
      (p) => p.id === recordingData.samples.fieldwork,
    )!;
    const coffeeOriginal = fieldwork.assets.find((a) => !a.parent_id)!;
    const coffeeBefore = fieldwork.runs.find(
      (r) => r.asset_id === coffeeOriginal.id,
    )!;
    const coffeeAfter = fieldwork.runs.find(
      (r) => r.asset_id !== coffeeOriginal.id,
    )!;
    expect(coffeeAfter.metrics!.attention_share).toBeLessThan(
      coffeeBefore.metrics!.attention_share,
    );
    expect(() => compareRecordedRuns(before, coffeeAfter)).toThrow(
      "same creative",
    );
    expect(() =>
      compareRecordedRuns(before, {
        ...after,
        model: { ...after.model!, centerbias: "other" },
      }),
    ).toThrow("same model");
  });
});
