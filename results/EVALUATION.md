# MirrorData — agent correctness evaluation

This file records the result of running a Claude Code agent over all 645 cases in
[`data/mirror_data.json`](../data/mirror_data.json) and judging, for each case,
**whether `candidate_code` satisfies its `description`**.

- Date: 2026-09-18
- Judge: Claude Code — Opus 5 orchestrator, Claude Sonnet 5 sub-agents
- Per-case results: [`agent_verdicts.json`](agent_verdicts.json), also as [CSV](agent_verdicts.csv)

## Headline result

| Verdict | Cases | Share |
|---|---:|---:|
| `correct` — would be accepted | 327 | 50.7% |
| `incorrect` — would be rejected | 318 | 49.3% |
| **Total** | **645** | |

Confidence: 641 high, 4 medium. The split is close to even, consistent with a
benchmark built to be label-free and non-trivial.

The 645 candidates cover **159 distinct task statements** (median 4 candidates each).
7 problems had all candidates correct, 11 had all candidates incorrect, and 141 were
mixed — so nearly every statement carries both passing and failing programs, and no
verdict can be inferred from a sibling.

## What "correct" means here

A case is `correct` only if the program, run as a standalone stdin→stdout solution,
would be **accepted** by the problem's judge:

1. Right answers on all valid inputs in the stated constraints — not just the samples.
2. Output format respected. Interactive prompt text (`"Enter n: "`), leftover debug
   prints, and missing/extra tokens fail. `YES`/`Yes`/`yes` differences and trailing
   whitespace are fine; so is extra *internal* whitespace, since judges compare tokens.
3. Fast enough for the stated constraints as CPython.
4. No crash on valid input.
5. Where the problem explicitly accepts **any** valid answer, any valid answer counts.
6. Incomplete code (a bare function with no I/O where stdin I/O is required, undefined
   names, truncation) fails.

## Method

**Stage 1 — mechanical sample testing.** Sample `Input`/`Output` blocks were extracted
from each statement (638 of 645 cases have one) and every candidate was executed
against them under a 10s timeout, compared token-wise and case-insensitively. Outcome:
392 pass, 234 mismatch, 12 crash, 7 no extractable sample.

**Stage 2 — judging.** Each case was judged with its statement, its code, and that
sample evidence in hand, with sample evidence treated as strong but **not** decisive.
Cases were grouped by shared statement so each problem was read once and its candidates
judged together. Where the answer is not unique, correctness was decided by checking
the problem's *conditions*, not by diffing the sample — using purpose-built validators,
brute-force references on small inputs, exhaustive enumeration of the whole input domain
where small enough (e.g. all 999 legal `x` for task 488, all 100 input pairs for task
549), and a spec-faithful interactor for the one interactive problem (tasks 633–634).

## Why sample tests alone are not enough

Sample outcome and final verdict agree on only **443 of 638** judgeable cases (69%).
Grading this dataset by sample-diffing would misclassify ~31% of it, in both directions.

- **130 cases pass every sample test and are still incorrect.** Causes: a greedy or
  formula that breaks off-sample (task 63 uses ±99999999 sentinels against coordinates
  up to 1e9; task 320 fails a random Kadane cross-check), float division losing
  precision near 1e9 (tasks 616, 618, 562), complexity blowups, a leftover `print(a)`
  debug line (task 72), or ignoring the test-case count entirely (task 549 hardcodes
  `range(10)`, so it is right only when `t` happens to be 10 — as in the sample).
- **65 cases fail a sample test and are nonetheless correct.** Nearly all are
  any-valid-answer problems where the program printed a different valid answer. Whole
  groups behave this way: all six of tasks 627–632 (bet distributions), 446/447/449
  (OR-maximising sequences), 498–502 (mod chains), 552/553/555 (string rearrangements),
  511 (Manhattan-distance point sets). Two further groups (432–435, 436–438) print a
  free operation count `m`, so only the claimed optimum `s` is fixed — these were judged
  by simulating the emitted operations. Task 633 is interactive, so its "crash" was an
  artifact of static input; a real interactor showed it answers correctly within the
  query limit over 84 games.

## Failure modes among the 318 incorrect cases

Approximate, from the recorded reasons: bugs found only off-sample (wrong greedy/DP,
off-by-one, n=1 or all-equal edge cases, float precision) ~165; wrong answer already
visible on the statement's own sample ~102; format/I-O handling (prompt text, debug
prints, hardcoded loop bounds, wrong ordering) ~26; produces no output at all ~11;
complexity/TLE ~4; crashes and recursion errors ~3.

## Data-quality findings about MirrorData itself

1. **Task_ids 364–370 (indices 363–369) have a corrupted `description`.** The field
   holds no task statement — it contains an unrelated Python file-generation utility
   (with Chinese comments), byte-identical across all seven records. These are exactly
   the 7 cases with no extractable sample; the `candidate_code` is intact and appears to
   solve a binary-string YES/NO task. They are judged `incorrect`: taking the description as the specification,
   it asks for a filesystem utility (scan numbered subfolders, count .html files, create
   matching -ac.py/-wa.py files), and all seven programs instead read stdin and classify
   binary strings, performing no filesystem operation at all. The verdict rests on the
   description being corrupt, so treat these seven as an artefact of the data rather than
   a finding about the programs.

2. **Every record carries a third field, `task_id`** (values 1–645, sequential), added
   by commits `c8b3a59` and `c7fba91`. The README still states each object has "exactly
   two fields" and that task and candidate IDs are excluded. `task_id` is only a
   sequential index and leaks no correctness label, but the README is now inaccurate.

Everything else in the README checks out: 645 cases, JSON array, both documented fields
present and non-empty on every record, no labels, counterexamples, test results, model
names or scores anywhere in the file, and 645 distinct (description, candidate_code) pairs.

## Caveats

- These are **judgements, not official verdicts.** There is no hidden test suite here; a
  `correct` verdict means no counterexample was found by reasoning, targeted tests,
  brute-force cross-checks, or exhaustive search where feasible. Absence of a
  counterexample is not proof.
- Time-limit calls are judgement calls. The 4 `medium`-confidence cases are
  performance-borderline (roughly 0.5–1.8s at worst-case input) with the real judge's
  limit unknown.
- Sample inputs were reconstructed from rendered statement text, which inserts a blank
  line between input lines; those blank lines were stripped before feeding programs.
- `index` is the 0-based position in the JSON array; `task_id` is the dataset's own field
  and equals `index + 1` throughout.

## Files

| File | Contents |
|---|---|
| `agent_verdicts.json` | Per-case verdict (correct/incorrect), confidence, reason, counterexample input, sample-test outcome |
| `agent_verdicts.csv` | Same, flattened for spreadsheets |
| `EVALUATION.md` | This report |
