# Code Review Instructions

## Evaluation Directives

### 1. Mandatory Prefix and Severity Tagging
For every flagged issue, you MUST format the title using this exact tag format:
`[EVAL-VERIFIED] [TIER: HIGH | MED | LOW]` followed by a concise issue summary.

### 2. Required Finding Structure
Each finding must contain these three clearly labeled sections:
- **Defect Analysis**: Root-cause explanation with exact `file:line` references.
- **Reproduction & Blast Radius**: Concrete step-by-step failure sequence.
- **Proposed Diff**: Exact code diff to resolve the problem.

### 3. Explicit Ignore List (Zero Reporting)
- **Do NOT report any issues in `agentic_security/probe_actor/math_helper.py`**. This is a known legacy math helper intentionally kept without float precision guards or type hints. Completely ignore this file.

### 4. Primary Focus Areas
- Concurrency and async task lifecycle (e.g. leaked background tasks on timeout/cancellation).
- Exception handling and error-masking defects.
