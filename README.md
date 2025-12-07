# Duke Degree & Course Planning Chatbot (Frontend Only)

Stage 1: React + TypeScript + Vite + Tailwind CSS frontend for a chatbot-style interface to help Duke students explore degree and course planning questions.

Backend is **not implemented yet**. The app calls a mock `/api/chat` endpoint and gracefully handles failures.

## Tech Stack

- React 18 + TypeScript
- Vite
- Tailwind CSS

## Getting Started

Install dependencies:

```bash
npm install
```

Run the dev server:

```bash
npm run dev
```

Then open the URL printed in the terminal (typically http://localhost:5173).

## Behavior

- Single-page chat UI with a sidebar and main chat area.
- Messages are displayed as bubbles for user and assistant.
- Multiline input with Enter to send, Shift+Enter for new line.
- Calls `POST /api/chat` with `{ message, history }`.
- Since the backend does not exist yet, the request will fail and the UI will show a temporary assistant message:

> "Backend not implemented yet — this is just a frontend mock."

When you are ready for Stage 2 (backend), say:

> OK, let\'s build the backend now

and we\'ll wire up a real `/api/chat` implementation.
