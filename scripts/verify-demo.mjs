import { createHash } from "node:crypto";
import { readFile, readdir } from "node:fs/promises";
import { dirname, resolve, relative } from "node:path";
import { fileURLToPath } from "node:url";
import assert from "node:assert/strict";

const root = resolve(
  dirname(fileURLToPath(import.meta.url)),
  "..",
  "frontend",
  "public",
);
const recording = JSON.parse(
  await readFile(resolve(root, "demo/manifest.json"), "utf8"),
);
assert.equal(recording.version, 1);
assert.equal(recording.mode, "recorded");
assert.equal(recording.projects.length, 3);
assert.equal(
  recording.model.source_commit,
  "c7db17e2d1d7ea6468ffdee2cfaddf141095dcff",
);
const expected = new Set(["demo/manifest.json"]);
let runs = 0;
for (const project of recording.projects) {
  assert.equal(project.assets.length, 2);
  assert.equal(project.runs.length, 2);
  for (const asset of project.assets) {
    assert.equal(asset.project_id, project.id);
    assert.equal(asset.confirmed, true);
    assert(asset.targets.length > 0 && asset.targets.length <= 8);
    for (const target of asset.targets) {
      assert.equal(target.box.length, 4);
      assert(target.box.every(Number.isInteger));
      const [left, top, right, bottom] = target.box;
      assert(left >= 0 && top >= 0 && left < right && top < bottom);
      assert(right <= asset.width && bottom <= asset.height);
      assert(["product", "headline", "logo", "cta", "other"].includes(target.role));
    }
    assert(recording.files[`/assets/${asset.id}/image`]);
  }
  for (const run of project.runs) {
    assert.equal(run.status, "completed");
    assert.deepEqual(run.model, recording.model);
    assert(
      project.assets.some(
        (asset) =>
          asset.id === run.asset_id && asset.sha256 === run.input_sha256,
      ),
    );
    assert(
      run.metrics.attention_share >= 0 && run.metrics.attention_share <= 1,
    );
    for (const artifact of ["heatmap.png", "overlay.png", "report.json"])
      assert(recording.files[`/runs/${run.id}/${artifact}`]);
    runs++;
  }
  assert(recording.files[`/projects/${project.id}/export`]);
}
for (const sample of ["forma", "fieldwork", "pace"])
  assert(
    recording.projects.some(
      (project) => project.id === recording.samples[sample],
    ),
  );
for (const file of Object.values(recording.files)) {
  assert(file.url.startsWith("/demo/"));
  const path = resolve(root, "." + file.url);
  assert(path.startsWith(resolve(root, "demo") + "/"));
  const bytes = await readFile(path);
  assert.equal(bytes.length, file.bytes, file.url);
  assert.equal(
    createHash("sha256").update(bytes).digest("hex"),
    file.sha256,
    file.url,
  );
  expected.add(relative(root, path));
}
async function inspect(directory) {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const path = resolve(directory, entry.name);
    assert(!entry.isSymbolicLink(), "No symlinks in public recordings");
    if (entry.isDirectory()) await inspect(path);
    else
      assert(
        expected.has(relative(root, path)),
        `Unexpected public file: ${path}`,
      );
  }
}
await inspect(resolve(root, "demo"));
console.log(
  `Verified 3 public samples, ${runs} genuine recorded analyses, and ${expected.size - 1} hashed artifacts.`,
);
