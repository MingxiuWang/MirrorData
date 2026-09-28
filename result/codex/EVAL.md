# MirrorData — Codex evaluation

This folder contains the Codex review of all 645 records in [`data/mirror_data.json`](../../data/mirror_data.json), judging whether each `candidate_code` satisfies its accompanying description.

## Result

| Verdict | Cases | Share |
|---|---:|---:|
| Satisfies description | 340 | 52.7% |
| Does not satisfy description | 305 | 47.3% |
| **Total** | **645** | |

## Method

The evaluation used `gpt-5.6-luna` and the same prompt-based static-review rule for every record. Candidate programs were not executed and no generated tests or reference solvers were used.

> Read the complete description, examples, constraints, and candidate_code. By ordinary static reasoning, decide whether the candidate code satisfies the description for all valid inputs. Check algorithm logic, required input/output, boundary cases, stated constraints, and obvious runtime failures. Mark false only when you can identify a concrete mismatch; otherwise mark true when the implementation reasonably appears correct.

These are model judgements rather than official judge verdicts.

## Files

| File | Contents |
|---|---|
| [`eval.json`](eval.json) | Evaluation method, universal prompt, summary, and detailed per-task verdicts with reasons |
| [`eval.csv`](eval.csv) | Flattened per-task verdicts and reasons |
| [`EVAL.md`](EVAL.md) | This overview |
