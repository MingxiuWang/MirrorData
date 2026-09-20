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
| `correct` — would be accepted | 315 | 48.8% |
| `incorrect` — would be rejected | 323 | 50.1% |
| `undetermined` — no usable specification | 7 | 1.1% |
| **Total** | **645** | |

Confidence: 635 high, 3 medium, 7 n/a. The split is close to even, consistent with a
benchmark built to be label-free and non-trivial. 23 of these verdicts were revised
during the adjudication pass described below.

The 645 candidates cover **159 distinct task statements** (median 4 candidates each).
4 problems had all candidates correct, 11 had all candidates incorrect, and 144 were
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

- **136 cases pass every sample test and are still incorrect.** Causes: a greedy or
  formula that breaks off-sample (task 63 uses ±99999999 sentinels against coordinates
  up to 1e9; task 320 fails a random Kadane cross-check), float division losing
  precision near 1e9 (tasks 616, 618, 562), complexity blowups, a leftover `print(a)`
  debug line (task 72), or ignoring the test-case count entirely (task 549 hardcodes
  `range(10)`, so it is right only when `t` happens to be 10 — as in the sample).
- **59 cases fail a sample test and are nonetheless correct.** Nearly all are
  any-valid-answer problems where the program printed a different valid answer. Whole
  groups behave this way: 446/447/449 (OR-maximising sequences), 498/499/500/502 (mod
  chains), 552/553/555 (string rearrangements), 511 (Manhattan-distance point sets), and
  three of the six bet-distribution candidates (628, 630, 631). The other three in that
  group (627, 629, 632) *also* print a valid-looking distribution but bust the `x_i <= 1e9`
  output bound on feasible inputs such as `k = [20]*10 + [19]*9`, so checking the
  problem's conditions has to include its output bounds, not just its objective. Two further groups (432–435, 436–438) print a
  free operation count `m`, so only the claimed optimum `s` is fixed — these were judged
  by simulating the emitted operations. Task 633 is interactive, so its "crash" was an
  artifact of static input; a real interactor showed it answers correctly within the
  query limit over 84 games.

## Failure modes among the 323 incorrect cases

Approximate, from the recorded reasons: bugs found only off-sample (wrong greedy/DP,
off-by-one, n=1 or all-equal edge cases, float precision) ~158; wrong answer already
visible on the statement's own sample ~101; format/I-O handling (prompt text, debug
prints, hardcoded loop bounds, wrong ordering) ~23; output-bound violations ~19;
produces no output at all ~10; complexity/TLE ~7; crashes ~4; a missing `flush` that
deadlocks an interactive problem ~1.

## Cross-check against an independent evaluation

This repository already contained `results/codex_evaluation.json`, an independent
evaluation of the same 645 cases (313 satisfies / 332 not). Comparing the two exposed
44 disagreements, and **every one of them was then adjudicated from scratch** by a
neutral pass that was told to trust neither stated reason and to verify by execution,
brute force, exhaustive enumeration, or a purpose-built interactor.

- **Agreement after adjudication: 614 of 638 judgeable cases (96.2%)** (before: 93.1%).
- **20 verdicts in this run were wrong and have been corrected.** The 24 that remain
  different from the Codex file are ones the adjudication confirmed in this run's favour.

The adjudication was worth doing: it changed 20 of 39 contested verdicts, and the errors
it caught were of kinds a single pass reliably misses.

**Errors corrected in this run (examples).**
- *A fabricated edge case.* Tasks 419/420/422 were failed on an all-zero input with the
  claim that the answer should be 1. The statement's own sample (p=(1,1,1,0) → 1) proves
  no game is played on an empty sequence, so 0 is right. All three match a brute-force DP
  over every count-vector and are now `correct`.
- *A group check that was too weak.* Tasks 627/629/632 were passed by a validator that
  tested the objective but whose random inputs never reached the feasible-large-product
  region. On `k = [20]*10 + [19]*9` they emit bets of 5.2e15–2.6e23, busting the
  `x_i <= 1e9` bound. Now `incorrect`.
- *Checking the sample but not the statement.* Task 187 returns 10 on the statement's own
  sample where the answer is 2; task 302's sentinel `10**12` is never overwritten when the
  true cost exceeds it; task 546 mishandles an eliminated carrier; task 544 crashes on the
  legal `.Q U/D/L/R` move of an uncarried Quaffle.
- *A protocol bug invisible to logic review.* Task 213's algorithm is provably correct, but
  its final answer is printed without `flush=True`, which deadlocks an interactive judge for
  t>1. Its sibling task 225 flushes and stays `correct`.

**Verdicts this run got right that the other evaluation did not (examples).** Task 359
prints the malformed `010:15 PM` for `22:15`; tasks 165/167/641 sort numbers as strings;
task 386 answers NO for `abacaba`, which splits as `ab|acaba`; task 602 returns 1 on
`[5,1,5]` where 5 is attainable; task 200 defines `solve()` and never calls it, printing
nothing; tasks 250 and 336 were failed by the other evaluation on inputs that the code
actually handles correctly.

The general lesson: a confidently-worded reason from either evaluation can be wrong in
either direction, and the statement's own sample is the most reliable tiebreaker.

## Data-quality findings about MirrorData itself

1. **Task_ids 364–370 (indices 363–369) have a corrupted `description`.** The field
   holds no task statement — it contains an unrelated Python file-generation utility
   (with Chinese comments), byte-identical across all seven records. These are exactly
   the 7 cases with no extractable sample. With no specification, "does the code satisfy
   the description" is unanswerable, so they are recorded as `undetermined` rather than
   guessed; the `candidate_code` is intact and appears to solve a binary-string YES/NO
   task. *(Note: the parallel Codex evaluation read these literally and marked all seven
   "does not satisfy", on the grounds that the code performs no filesystem operations.
   That is a defensible alternative reading; under it, this run's totals would be 327
   correct / 330 incorrect.)*

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
- Time-limit calls are judgement calls. The 3 remaining `medium`-confidence cases are
  performance-borderline (roughly 0.5–1.8s at worst-case input) with the real judge's
  limit unknown; a fourth (task 494) was resolved to `incorrect` during adjudication on
  measured worst-case timing.
- Sample inputs were reconstructed from rendered statement text, which inserts a blank
  line between input lines; those blank lines were stripped before feeding programs.
- `index` is the 0-based position in the JSON array; `task_id` is the dataset's own field
  and equals `index + 1` throughout.

## Files

| File | Contents |
|---|---|
| `agent_verdicts.json` | Per-case verdict, confidence, reason, counterexample input, sample-test outcome |
| `agent_verdicts.csv` | Same, flattened for spreadsheets |
| `EVALUATION.md` | This report |
