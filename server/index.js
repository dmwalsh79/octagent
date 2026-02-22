import "dotenv/config";
import express from "express";
import path from "node:path";
import apiRouter from "./routes/api.js";

const app = express();
const port = Number(process.env.PORT || 3000);

app.use(express.json({ limit: "1mb" }));
app.use("/api", apiRouter);
app.use(express.static(path.resolve("public")));

app.get("*", (_req, res) => {
  res.sendFile(path.resolve("public", "index.html"));
});

app.listen(port, () => {
  console.log(`Board Assistant running on http://localhost:${port}`);
});
