# ADR 0001: Next.js frontend with FastAPI backend

- Status: Accepted
- Context: Project brief specifies independently deployable Next.js/Vercel frontend and Python ML backend.
- Decision: Use Next.js App Router and TypeScript; keep validation, preprocessing, inference and reliability logic in FastAPI.
- Consequences: Separate deployments and environment configuration are required; the frontend cannot make authoritative predictions.
