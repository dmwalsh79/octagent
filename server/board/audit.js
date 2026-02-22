import fs from "node:fs/promises";
import path from "node:path";

const auditPath = path.resolve("data", "audit-log.jsonl");

export async function appendAudit(event) {
  const line = `${JSON.stringify({ ts: new Date().toISOString(), ...event })}\n`;
  await fs.mkdir(path.dirname(auditPath), { recursive: true });
  await fs.appendFile(auditPath, line, "utf8");
}
