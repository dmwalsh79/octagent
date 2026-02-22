import fs from "node:fs/promises";
import path from "node:path";
import { requestWithFallback } from "./aiClient.js";
import { appendAudit } from "./audit.js";
import { boardMemberPrompt, chairmanPrompt } from "./prompts.js";

const personalitiesPath = path.resolve("server", "board", "personalities.json");

function parseJsonSafely(text, fallback) {
  try {
    return JSON.parse(text);
  } catch {
    return fallback;
  }
}

async function loadPersonalities() {
  const raw = await fs.readFile(personalitiesPath, "utf8");
  const all = JSON.parse(raw);
  const chairman = all.find((p) => p.isChairman);
  const voters = all.filter((p) => !p.isChairman);
  if (!chairman || voters.length !== 7) {
    throw new Error("Personalities config must have 1 chairman and 7 voters");
  }
  return { chairman, voters, all };
}

function finalFromVotes(votes, chairmanDecision) {
  const approve = votes.filter((v) => v.stance === "approve").length;
  const reject = votes.length - approve;
  const majorityVerdict = approve >= 4 ? "approve" : "reject";

  const veto = Boolean(chairmanDecision?.veto);
  let verdict = majorityVerdict;

  if (veto) {
    verdict = majorityVerdict === "approve" ? "reject" : "reject";
  }

  if (!veto && chairmanDecision?.verdict && chairmanDecision.verdict !== majorityVerdict) {
    verdict = majorityVerdict;
  }

  return {
    approve,
    reject,
    majorityVerdict,
    finalVerdict: verdict,
    veto
  };
}

export async function runBoardDecision({ userInput, taskType = "general" }) {
  const { chairman, voters } = await loadPersonalities();

  const primary = process.env.MODEL_PRIMARY || "gpt-4o-mini";
  const fallback = process.env.MODEL_FALLBACK || "gpt-4.1-mini";
  const chairmanModel = process.env.CHAIRMAN_MODEL || primary;

  const votePromises = voters.map(async (member) => {
    const systemPrompt = boardMemberPrompt(member);
    const userPrompt = `Task type: ${taskType}\nUser request: ${userInput}`;
    const response = await requestWithFallback({
      models: [primary, fallback],
      systemPrompt,
      userPrompt,
      retriesPerModel: 3,
      baseDelayMs: 600
    });

    const parsed = parseJsonSafely(response.text, {
      stance: "reject",
      confidence: 0,
      reasoning: "Invalid JSON from model",
      action_plan: [],
      risks: ["Model returned malformed output"]
    });

    return {
      memberId: member.id,
      memberName: member.name,
      ...parsed,
      modelUsed: response.usedModel
    };
  });

  const votes = await Promise.all(votePromises);

  const approve = votes.filter((v) => v.stance === "approve").length;
  const reject = votes.length - approve;
  const majorityVerdict = approve >= 4 ? "approve" : "reject";

  const chairmanInput = {
    userInput,
    taskType,
    votes,
    summary: {
      approve,
      reject,
      majorityVerdict
    }
  };

  const chairmanResponse = await requestWithFallback({
    models: [chairmanModel, primary, fallback],
    systemPrompt: chairmanPrompt(chairman),
    userPrompt: JSON.stringify(chairmanInput),
    retriesPerModel: 3,
    baseDelayMs: 700,
    temperature: 0.2
  });

  const chairmanDecision = parseJsonSafely(chairmanResponse.text, {
    veto: true,
    verdict: "reject",
    chairman_reason: "Chairman model returned malformed output",
    conditions: ["Retry request"]
  });

  const summary = finalFromVotes(votes, chairmanDecision);
  const decision = {
    request: userInput,
    taskType,
    summary,
    chairman: {
      ...chairmanDecision,
      modelUsed: chairmanResponse.usedModel
    },
    votes
  };

  await appendAudit({ type: "board_decision", decision });
  return decision;
}
