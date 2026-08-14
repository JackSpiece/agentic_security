# Full Project Review Instructions & Feature Architecture Audit

## Scope of this review

This pull request presents the entire project (199 files) against an empty base commit (`review-base-empty`), so every file is visible in the diff payload.

Treat this review as a dual-purpose audit:
1. **Full-Codebase System Audit**: Identify cross-module contract bugs, correctness bugs, and security issues across existing modules.
2. **New Feature Architecture & Concurrency Critique**:
   - Critically inspect the newly added `agentic_security/probe_actor/rate_limiter.py` (Async Token Bucket Rate Limiter & Concurrency Governor).
   - Evaluate whether the lock acquisition, token calculation, and adaptive backoff have any race conditions, deadlocks under high concurrency, or drift under event-loop load.
   - Propose architectural extensions, edge cases, and additional features that would make the rate-limiting and probing engine more robust.

## What to report

Prioritise, in order:
1. Correctness & Concurrency bugs: race conditions, deadlocks, drift in timing math, unhandled cancellation in async locks.
2. Cross-module contract violations across the full codebase.
3. Security issues: credential handling, injection, unauthorized exposure.
4. Architectural suggestions & feature enhancement ideas for the probing engine.

## Verification bar
Cite `file:line` for any claim and provide concrete step-by-step proofs for any flagged defects.
