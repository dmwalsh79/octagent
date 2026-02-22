# Board Assistant (8-Personality AI)

An AI personal assistant that behaves like a board:
- 7 voting members (different personalities)
- 1 chairman with veto power
- Majority rule for approval/rejection
- Governed self-modification (board votes before applying changes)

## Why this model setup
Recommended default stack:
- `gpt-4o-mini` for all voting personalities (best cost/speed balance for multi-agent orchestration)
- `gpt-4o` for chairman (higher reliability for veto/safety judgment)
- `gpt-4.1-mini` fallback for transient or rate-limit failures

This project includes retry + exponential backoff + model fallback routing to handle 429/rate-limit and transient API errors.

## Folder structure

```
.
├── public/
│   ├── index.html        # Landing page UI
│   ├── styles.css        # Styling
│   └── app.js            # Browser logic for ask + self-modify
├── server/
│   ├── index.js          # Express server bootstrap
│   ├── routes/
│   │   └── api.js        # API endpoints
│   └── board/
│       ├── personalities.json  # 8 personality definitions
│       ├── prompts.js          # System prompt templates
│       ├── aiClient.js         # AI calls + retries + fallback
│       ├── boardEngine.js      # Majority + chairman veto orchestration
│       ├── selfModify.js       # Governed self-editing scope
│       └── audit.js            # JSONL audit logging
├── data/
│   └── audit-log.jsonl    # Runtime decision/audit events (generated)
├── .env.example
├── package.json
└── README.md
```

## Quick start

1. Install dependencies
```bash
npm install
```

2. Configure environment
```bash
cp .env.example .env
# then edit .env with your OPENAI_API_KEY
```

3. Run
```bash
npm run dev
```

4. Open
- `http://localhost:3000`

## API

### `POST /api/ask`
Body:
```json
{
  "question": "Should we launch this feature next week?",
  "taskType": "product"
}
```

Returns: votes from 7 members, chairman decision, majority summary, veto status, and final verdict.

### `POST /api/self-modify`
Body:
```json
{
  "governanceQuestion": "Should we update the architect style prompt?",
  "proposal": {
    "targetPersonalityId": "architect",
    "appendToStyle": "Prioritize API contract tests in all plans."
  }
}
```

If and only if board governance approves (and chairman does not veto), a controlled edit is applied to `server/board/personalities.json`.

## Safety constraints on self-modification

- Edits are scoped to one file (`SELF_MOD_SCOPE`, default `server/board/personalities.json`)
- Proposal format is restricted to style append actions
- All decisions are audit-logged to `data/audit-log.jsonl`

## Notes

- This is a strong starter architecture for a board-style assistant.
- For production use, add auth, request quotas, stronger policy filters, durable queueing, and full test coverage.
