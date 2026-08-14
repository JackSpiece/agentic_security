# Agentic Security Architecture Overview

This document describes the core architecture and pipeline of Agentic Security.

## System Architecture

Agentic Security is structured into four primary components:

1. **API & Web Interface (`agentic_security.app`)**
   - FastAPI server serving static UI and REST endpoints.
   - Streaming endpoints for real-time vulnerability scan progress.

2. **Probe Actor / Fuzzer Engine (`agentic_security.probe_actor`)**
   - Dispatches probe payloads across text, image, and audio modalities.
   - Evaluates LLM responses using refusal heuristics and classifier pipelines.

3. **Probe Datasets (`agentic_security.probe_data`)**
   - Built-in adversarial datasets (jailbreaks, prompt injections, PII extraction).
   - Registry for custom and dynamically generated attack vectors.

4. **Reporting & Export (`agentic_security.routes.report`)**
   - Generates CSV exports (`failures.csv`, `full_scan_log.csv`) and graphical metric charts.

## Example Python Usage

```python
import asyncio
from agentic_security.probe_data.data import prepare_prompts
from agentic_security.primitives import Scan

# Prepare prompt suite for selected datasets
prompts = prepare_prompts(dataset_names=["AgenticBackend"], budget=100)
print(f"Loaded {len(prompts)} prompts for evaluation.")
```
