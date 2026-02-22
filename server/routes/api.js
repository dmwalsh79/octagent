import express from "express";
import { runBoardDecision } from "../board/boardEngine.js";
import { applyGovernedSelfModification } from "../board/selfModify.js";

const router = express.Router();

router.get("/health", (_req, res) => {
  res.json({ ok: true, service: "board-assistant" });
});

router.post("/ask", async (req, res) => {
  try {
    const { question, taskType } = req.body || {};
    if (!question || typeof question !== "string") {
      return res.status(400).json({ error: "question is required" });
    }

    const decision = await runBoardDecision({ userInput: question, taskType: taskType || "general" });
    return res.json(decision);
  } catch (err) {
    return res.status(500).json({
      error: "Failed to process board decision",
      details: err.message
    });
  }
});

router.post("/self-modify", async (req, res) => {
  try {
    const { proposal, governanceQuestion } = req.body || {};
    if (!proposal || typeof proposal !== "object") {
      return res.status(400).json({ error: "proposal object is required" });
    }

    const boardDecision = await runBoardDecision({
      userInput: governanceQuestion || `Should we apply this codebase self-modification proposal? ${JSON.stringify(proposal)}`,
      taskType: "self-modification"
    });

    const modResult = await applyGovernedSelfModification({ proposal, boardDecision });

    return res.json({ boardDecision, modResult });
  } catch (err) {
    return res.status(500).json({
      error: "Failed to process self modification",
      details: err.message
    });
  }
});

export default router;
