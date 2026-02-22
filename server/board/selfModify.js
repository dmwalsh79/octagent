import fs from "node:fs/promises";
import path from "node:path";
import { appendAudit } from "./audit.js";

const DEFAULT_SCOPE = "server/board/personalities.json";

function resolveScope() {
  return path.resolve(process.env.SELF_MOD_SCOPE || DEFAULT_SCOPE);
}

export async function applyGovernedSelfModification({ proposal, boardDecision }) {
  const scopePath = resolveScope();
  const finalVerdict = boardDecision?.summary?.finalVerdict;
  const veto = boardDecision?.summary?.veto;

  if (finalVerdict !== "approve" || veto) {
    return {
      applied: false,
      reason: "Board did not approve modification"
    };
  }

  const current = await fs.readFile(scopePath, "utf8");
  const config = JSON.parse(current);

  const targetId = proposal?.targetPersonalityId;
  const promptAddition = proposal?.appendToStyle;

  if (!targetId || !promptAddition) {
    return { applied: false, reason: "Proposal missing targetPersonalityId or appendToStyle" };
  }

  const index = config.findIndex((p) => p.id === targetId);
  if (index < 0) {
    return { applied: false, reason: `Personality ${targetId} not found` };
  }

  config[index].style = `${config[index].style} ${promptAddition}`.trim();
  await fs.writeFile(scopePath, `${JSON.stringify(config, null, 2)}\n`, "utf8");

  await appendAudit({
    type: "self_modification_applied",
    proposal,
    target: targetId,
    scopePath
  });

  return { applied: true, target: targetId, scopePath };
}
