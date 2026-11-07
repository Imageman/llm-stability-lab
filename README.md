# LLM Stability Lab

A small, reproducible pilot framework for measuring how answers change under repeated requests, irrelevant
context, harmless wording changes, and multiple-choice answer shuffling. Prompts and reports are in English;
CLI logs are in English.

The complete English research report, including experiment results and links to the local raw data, is in
[raw_report.md](raw_report.md). A Russian-language report is available in [README_ru.md](README_ru.md).

## Setup

Use Python 3.11 or newer. In PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Edit `configs/default.yaml` to match the endpoint and exact model ID exposed by LM Studio. The default endpoint is
`http://192.168.0.109:1234/v1` and the selected model ID is `openai/gpt-oss-20b`. The application lists available
IDs and reports a mismatch; it never silently selects another model. It does not download models.

All implementation modules live directly under `src\`. The editable package mapping keeps the documented
`python -m llm_stability_lab` command available without a nested source directory.

## Commands

```powershell
# List model IDs reported by /v1/models
python -m llm_stability_lab models

# Preview the default plan and a few rendered prompts without sending requests
python -m llm_stability_lab plan

# Print every request and prompt in the plan
python -m llm_stability_lab plan --preview-all

# Run a small deterministic debugging sample
python -m llm_stability_lab run --experiment 01 --task task_01_math --repetitions 2

# Override the model ID and experimental seed
python -m llm_stability_lab run --experiment 04 --model "server-exposed-model-id" --seed 73

# Send one request to LM Studio and save its response
python -m llm_stability_lab smoke --task task_01_math

# Run all five experiments with the configured defaults
python -m llm_stability_lab run

# Resume an interrupted run with the same options
python -m llm_stability_lab run --resume RUN_ID

# Build reports from a saved run ID or a JSONL file path
python -m llm_stability_lab report RUN_ID
```

`run` is the only command that launches a full experiment plan. Its default plan contains 621 inference calls:
300 for determinism and 321 across the remaining four experiments. Review `plan` before a full run. Override the
selected experiment, task list, repetition count, permutation count, or interaction block count from the CLI.

## Experiments

| ID | Experiment | Design |
| --- | --- | --- |
| 01 | Determinism | Repeats the same stateless prompt 100 times per task by default. |
| 02 | Position sensitivity | Compares clean prompts with three fixed noise samples at three insertion positions. |
| 03 | Reasoning stability | Uses unrelated words, irrelevant sentences, neutral wording, and varied noise lengths. |
| 04 | Answer-order sensitivity | Tests all 24 logical-task orders and 90 balanced traffic-task orders by default. |
| 05 | Noise x answer order | Matched clean/noisy and original/shuffled conditions with balanced positions. |
| 06 | Noise length x answer order | Measures errors across configurable lengths using the selected model tokenizer. |

Experiment 06 is selected explicitly, so the default `run` still executes experiments 01–05. It uses a clean
baseline and noise targets of 256, 1,024, 4,096, and 8,192 model tokens. By default, each level uses the same repeated
word sequence, and each block matches original and shuffled answer orders across lengths. With one block there is
one noise position and one shuffled order per task; use more blocks to cover positions and answer orders.

```powershell
python -m llm_stability_lab plan --experiment 06 --model google/gemma-4-26b-a4b --interaction-blocks 1
python -m llm_stability_lab run --experiment 06 --model google/gemma-4-26b-a4b --interaction-blocks 1
```

Planning experiment 06 connects to the LM Studio SDK and may load the selected model. The SDK tokenizes the actual
noise and formatted chat. The configured context limit is 18,000 tokens, including the `max_tokens` generation
reserve (2,048 by default) and an extra 64-token template margin. Server-reported input token counts are saved for
comparison. Configure `experiment_6_noise_levels` and `experiment_6_context_limit` in the YAML file. The default
18 blocks produce 360 requests across both tasks; the one-block command above produces 20 requests. Set
`experiment_6_noise_variant` to `random_words`, `sentences`, or `catalog` to generate other reproducible noise;
`experiment_6_noise_seed` controls its random seed independently of answer order. Set `experiment_6_noise_file`
to a JSON mapping from target lengths to exact text to reuse the same noise across models. Each model measures that
text with its own tokenizer; noise above 8,192 tokens is rejected.

Correctness is evaluated locally. Multiple-choice answers map to stable semantic choice IDs, so a changed displayed
number does not count as a changed answer when it still names the same choice. Temperature zero is sent explicitly.
If the API rejects a requested parameter, the failed request and traceback are saved; there is no fallback to a
different setting. SDK retries default to zero.

## Results and interpretation

Each run receives a unique ID. Raw JSONL is appended after every request under `results/raw/`; run configuration and
plan hashes are saved under `results/runs/`; logs are under `results/logs/`. Resume validates the saved settings and
plan and skips every case already recorded, including failed requests. Reports are written to a new timestamped
directory under `results/reports/` with CSV tables, Markdown results, and PNG charts.

This is a small pilot with three hand-written tasks. Repeated calls and prompt variants are not independent reasoning
problems. The report keeps task-level results separate and omits cluster-bootstrap intervals when there are too few
independent task clusters. Results do not establish general model robustness. The API response can report the
selected model and available usage, but an accepted request does not prove that the backend applied every requested
generation setting exactly.

## Tests

Run mocked unit tests without a server:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

The tests cover task answers, answer permutations, perturbation reproducibility, evaluation, case planning,
incremental JSONL persistence, resume validation, reporting, and mocked inference. A live `smoke` command is
optional and sends one prompt to the configured server.

To enable the separate live integration test explicitly:

```powershell
$env:LLM_STABILITY_LAB_INTEGRATION = "1"
.\.venv\Scripts\python.exe -m pytest tests/test_lm_studio_integration.py
```
