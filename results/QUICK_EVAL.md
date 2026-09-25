# MirrorData — quick-judge evaluation

Every case in [`data/mirror_data.json`](../data/mirror_data.json) judged for whether
`candidate_code` solves its `description`.

- Date: 2026-09-26
- Judge: Claude Code (Claude Sonnet 5 workers, one orchestrator)
- Results: [`quick_eval.json`](quick_eval.json), [`quick_eval.csv`](quick_eval.csv)

## Result

| Verdict | Cases |
|---|---:|
| `correct` | 319 (49.5%) |
| `incorrect` | 326 (50.5%) |
| **Total** | **645** |

Across the 159 distinct task statements: 7 had all candidates judged correct, 17 all
incorrect, 135 mixed.

## Method

Deliberately a **quick reading-based judgement**, not a verification pipeline.

- **One universal prompt** applied to all 645 cases, with no per-problem tailoring.
- **No code execution.** The prompt forbids running the candidate, writing test scripts,
  writing brute-force or reference implementations, and hand-simulating the program
  against the sample. Verdicts come from reading the statement and the code.
- **Limited tools:** one read of the input, one write of the output.
- **Binary and fast:** `correct` or `incorrect`, no third option and no "unsure"; snap
  judgement expected, with instructions not to dwell on hard cases.
- Work was split into 43 chunks of 15 cases. Cases sharing a statement sit together, so
  a judge reads each statement once and rules on its candidates as a group — which
  makes near-duplicate candidates easy to compare against each other.

The bar applied: right answers on all inputs within the stated constraints (not just the
sample), correct output format, fast enough for the stated limits, no crashes; and where
a statement accepts any valid answer, any valid answer counts.

## What this is and is not

This is a **baseline measurement of a quick LLM judgement**, so it should be read as
noisy. Individual verdicts are not verified and are wrong in both directions: the judges
had no way to execute anything, so bugs that only surface on a specific input, and
performance limits, rest on reasoning alone. Several reports noted candidates that pass
the statement's sample but were judged incorrect on a hand-constructed input, and those
calls carry real uncertainty. No verdict here was revisited or repaired after the fact.

Two operational notes for reproducibility:

- Fifteen cases (indices 255–269, the "Bessie's Birthday Cake" group plus neighbours)
  are the one exception to the worker setup. Three successive Sonnet workers failed on
  that chunk — one exceeded the 64K output-token limit, two stalled — so the
  orchestrator model judged those fifteen directly, under the same prompt and the same
  no-execution rule.
- Task_ids 364–370 share a corrupted `description`: instead of a task statement the
  field holds an unrelated Python filesystem script. Judged against that text as the
  specification, the candidates (which read stdin and classify binary strings) do not
  implement it. Those seven verdicts say more about the data than about the programs.

## Files

| File | Contents |
|---|---|
| `quick_eval.json` | Per-case `task_id`, `index`, `verdict`, short `reason` |
| `quick_eval.csv` | Same, flattened |
| `QUICK_EVAL.md` | This note |

`index` is the 0-based position in the JSON array; `task_id` equals `index + 1`.
