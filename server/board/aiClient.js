import process from "node:process";

const RETRYABLE_STATUS = new Set([408, 409, 425, 429, 500, 502, 503, 504]);

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function isRateLimitOrTransient(err) {
  if (!err || typeof err !== "object") {
    return false;
  }
  return RETRYABLE_STATUS.has(err.status || 0);
}

function normalizeError(status, bodyText) {
  const err = new Error(`AI request failed with status ${status}`);
  err.status = status;
  err.body = bodyText;
  return err;
}

export async function requestChat({ model, systemPrompt, userPrompt, temperature = 0.4 }) {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    throw new Error("OPENAI_API_KEY is not configured");
  }

  const baseUrl = process.env.OPENAI_BASE_URL || "https://api.openai.com/v1";
  const url = `${baseUrl.replace(/\/$/, "")}/chat/completions`;

  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`
    },
    body: JSON.stringify({
      model,
      temperature,
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: userPrompt }
      ],
      response_format: { type: "json_object" }
    })
  });

  const text = await response.text();
  if (!response.ok) {
    throw normalizeError(response.status, text);
  }

  const data = JSON.parse(text);
  const message = data?.choices?.[0]?.message?.content;
  if (!message) {
    throw new Error("Model returned no content");
  }

  return { raw: data, text: message, model };
}

export async function requestWithFallback({
  models,
  systemPrompt,
  userPrompt,
  retriesPerModel = 3,
  baseDelayMs = 500,
  temperature
}) {
  let lastError;

  for (const model of models.filter(Boolean)) {
    for (let attempt = 1; attempt <= retriesPerModel; attempt += 1) {
      try {
        const res = await requestChat({ model, systemPrompt, userPrompt, temperature });
        return { ...res, attempt, usedModel: model };
      } catch (err) {
        lastError = err;
        if (!isRateLimitOrTransient(err) || attempt === retriesPerModel) {
          continue;
        }
        const jitter = Math.floor(Math.random() * 200);
        const delay = baseDelayMs * 2 ** (attempt - 1) + jitter;
        await sleep(delay);
      }
    }
  }

  throw lastError || new Error("All model fallbacks failed");
}
