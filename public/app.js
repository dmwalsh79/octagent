const askBtn = document.getElementById("askBtn");
const selfModBtn = document.getElementById("selfModBtn");
const questionEl = document.getElementById("question");
const taskTypeEl = document.getElementById("taskType");
const decisionEl = document.getElementById("decision");
const targetEl = document.getElementById("targetPersonality");
const appendEl = document.getElementById("appendStyle");
const selfModResultEl = document.getElementById("selfModResult");

function pretty(value) {
  return JSON.stringify(value, null, 2);
}

askBtn.addEventListener("click", async () => {
  const question = questionEl.value.trim();
  if (!question) {
    decisionEl.textContent = "Please enter a question first.";
    return;
  }

  askBtn.disabled = true;
  askBtn.textContent = "Board deliberating...";

  try {
    const response = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question,
        taskType: taskTypeEl.value
      })
    });

    const data = await response.json();
    decisionEl.textContent = pretty(data);
  } catch (err) {
    decisionEl.textContent = `Error: ${err.message}`;
  } finally {
    askBtn.disabled = false;
    askBtn.textContent = "Ask the Board";
  }
});

selfModBtn.addEventListener("click", async () => {
  const targetPersonalityId = targetEl.value.trim();
  const appendToStyle = appendEl.value.trim();

  if (!targetPersonalityId || !appendToStyle) {
    selfModResultEl.textContent = "Both target personality and style addition are required.";
    return;
  }

  selfModBtn.disabled = true;
  selfModBtn.textContent = "Submitting proposal...";

  try {
    const response = await fetch("/api/self-modify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        governanceQuestion: `Should the board append this style rule to ${targetPersonalityId}? ${appendToStyle}`,
        proposal: { targetPersonalityId, appendToStyle }
      })
    });

    const data = await response.json();
    selfModResultEl.textContent = pretty(data);
  } catch (err) {
    selfModResultEl.textContent = `Error: ${err.message}`;
  } finally {
    selfModBtn.disabled = false;
    selfModBtn.textContent = "Propose Self-Modification";
  }
});
