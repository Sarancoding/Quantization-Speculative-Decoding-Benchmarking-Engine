// Freebuff build shim ("build" npm script).
//
// Regenerates the analysis artifacts (metrics, Pareto chart, writeup, PDFs)
// when the pinned Python stack is available; otherwise it is a no-op because
// the artifacts are already generated and committed. Always exits 0 so the
// platform's build step succeeds for this docs/artifact project.
import { spawnSync } from "node:child_process";

const candidates = [".venv/bin/python", "python3"];
let py = null;
for (const candidate of candidates) {
  const probe = spawnSync(candidate, ["-c", "import numpy, matplotlib, fpdf"], {
    encoding: "utf8",
  });
  if (probe.status === 0) {
    py = candidate;
    break;
  }
}

if (!py) {
  console.log(
    "[build] Python analysis stack not installed; using committed artifacts."
  );
  process.exit(0);
}

console.log(`[build] regenerating artifacts with ${py}`);
const run = spawnSync(py, ["-m", "orchestrator.pipeline", "--mode", "simulate"], {
  encoding: "utf8",
  stdio: "inherit",
});
process.exit(run.status === null ? 1 : run.status);
