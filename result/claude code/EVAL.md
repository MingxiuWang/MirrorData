# MirrorData — isolated per-task evaluation

Each case in [`data/mirror_data.json`](../data/mirror_data.json) judged for whether
`candidate_code` solves its `description`.

- Date: 2026-09-27
- Model: `claude-sonnet-5`, effort `low`, thinking disabled
- Prompt: [`prompt.md`](prompt.md) · Runner: [`run_eval.py`](run_eval.py) · Settings: [`settings.json`](settings.json) · Results: [`eval.json`](eval.json), [`eval.csv`](eval.csv)

## Result

| Verdict | Cases |
|---|---:|
| `correct` | 128 (19.8%) |
| `incorrect` | 517 (80.2%) |
| **Total** | **645** |

Runtime 91 s wall clock, 12 workers. 1,009,113 input + 8,774 output tokens, about $2.11.

## Isolation

Every task is judged **completely independently**. Nothing carries from one to the next.

- Each task is materialised as its own environment holding **only** `description.txt` and
  `candidate.py` for that task.
- One **stateless API call** per task. The request contains the system prompt and that
  single task's two files — no other task, no conversation history, no accumulated notes.
- **No memory between tasks.** There is nothing to clear: no state survives a call, so a
  judgement can never be informed by, or compared against, another task.
- **No tools of any kind**, so no web search, no code execution, no filesystem access.
  The verdict comes from reading the description and the program.
- Tasks are processed concurrently, but concurrency shares no state — worker threads only
  write their own result file.

This matters for this dataset: the 645 candidates cover only 159 distinct problems, so
several programs share a statement. A judge that sees siblings together can diff
near-duplicates and infer which one carries an injected bug. Judging each task alone
removes that signal, which is the point.

## Prompt

One universal system prompt, identical for all 645 tasks, with no per-problem tailoring:

> You judge whether a Python program is a correct solution to a programming task.
> Judge it as a competitive-programming submission: it must give right answers for all
> inputs allowed by the stated constraints (not just the example in the statement), print
> output in the required format, run fast enough for the stated limits, and not crash. If
> the statement says any valid answer is accepted, any valid answer counts.
> This is a quick judgement - do not deliberate at length.

The reply is constrained by a JSON schema to `{"verdict": "correct" | "incorrect"}`, so
every case gets one of the two labels and the model cannot answer with prose.

## Reading the numbers

The split is heavily skewed to `incorrect` (80%). That is a property of this
configuration, not a claim about the dataset: a fast, low-effort judge that cannot run
anything resolves uncertainty by calling a program wrong. Anything it cannot quickly
convince itself is right tends to land in `incorrect`, so expect many false `incorrect`
labels and relatively few false `correct` ones.

At the problem level, of the 159 distinct statements, 5 had every candidate judged
correct and 90 had every candidate judged incorrect.

These are unverified snap judgements and are wrong in both directions by construction. No
verdict was reviewed, re-run, or repaired after the fact.

## Reproducing

`run_eval.py` expects `ANTHROPIC_API_KEY`, builds one directory per task, and writes one
result file per task; it skips tasks already done, so it can be re-run to resume.

## Files

| File | Contents |
|---|---|
| `eval.json` | Per-case `task_id`, `index`, `verdict` |
| `eval.csv` | Same, flattened |
| `run_eval.py` | The runner |
| `prompt.md` | The exact prompt sent for every case, plus the response schema |
| `settings.json` | Exact run configuration: model, effort, prompt, isolation, usage |
| `EVAL.md` | This note |

`index` is the 0-based position in the JSON array; `task_id` equals `index + 1`.
