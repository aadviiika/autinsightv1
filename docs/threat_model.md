# Threat model

## Assets and risks

Inputs may reveal sensitive child developmental and demographic information. Risks include accidental collection of identifiers, request logging, model artifact substitution, exposure of an unauthenticated prediction endpoint, misleading interpretation, malformed inputs, and deployment misconfiguration.

## Current mitigations

The UI instructs users not to enter identifying information; API schema validates age and binary responses; CORS is configured through an origin allowlist; raw data and model artifacts are git-ignored; the app does not intentionally persist request bodies; result text distinguishes screening from diagnosis.

## Remaining work

No authentication, rate limiting, transport policy, formal privacy assessment, retention controls, audit logging policy, or clinical governance is implemented. Hosting logs may contain request metadata. Before public access, enforce HTTPS, least-privilege hosting, restricted CORS, rate limits, monitoring, non-retention of payloads, vulnerability review, and appropriate ethics/privacy approval. Only load trusted joblib artifacts because deserialization can execute code.
