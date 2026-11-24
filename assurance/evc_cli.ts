import { readFileSync } from "node:fs";
import { evaluateGraph, loadGraph } from "./evc";

const path = process.argv[2];
if (!path) {
  process.stderr.write("Usage: evc_cli <graph.json>\n");
  process.exit(2);
}
try {
  const graph = loadGraph(readFileSync(path));
  process.stdout.write(JSON.stringify(evaluateGraph(graph)) + "\n");
} catch (error) {
  const message = error instanceof Error ? error.message : "Unknown EVC error";
  process.stderr.write(message + "\n");
  process.exit(1);
}
