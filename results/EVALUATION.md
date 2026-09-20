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
| `incorrect` — would be rejected | 311 | 48.2% |
| `undetermined` — no usable specification | 7 | 1.1% |
| **Total** | **645** | |

Confidence: 634 high, 4 medium, 7 n/a. The split is close to even, consistent with a
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

## Failure modes among the 311 incorrect cases

Approximate, from the recorded reasons: bugs found only off-sample (wrong greedy/DP,
off-by-one, n=1 or all-equal edge cases, float precision) ~165; wrong answer already
visible on the statement's own sample ~102; format/I-O handling (prompt text, debug
prints, hardcoded loop bounds, wrong ordering) ~26; produces no output at all ~11;
complexity/TLE ~4; crashes and recursion errors ~3.

## Cross-check against an independent evaluation

This repository already contained `results/codex_evaluation.json`, an independent
evaluation of the same 645 cases (313 satisfies / 332 not). Comparing the two:

- **Agreement: 594 of 638 judgeable cases (93.1%).**
- 44 cases still disagree. A sample of 8 was adjudicated from scratch this session by
  brute force and execution:
  - **3 corrections were applied to this run** (tasks 419, 420, 422). A sub-agent had
    failed them on an all-zero input, claiming the answer should be 1; the statement's
    own sample (p=(1,1,1,0) → 1) proves no game is played on an empty sequence, so 0 is
    right. All three match a brute-force DP over every count-vector up to 4 and a
    DP-validated formula up to the constraint limit of 200. These are now `correct`.
  - **5 were confirmed in favour of this run** (tasks 167, 359, 386, 602, 641), each by
    running the program: task 359 prints the malformed `010:15 PM` for `22:15`; task 167
    sorts numbers as strings and scores 13 where 11 is optimal; task 641 never converts
    to int and answers NO where YES is right; task 602 returns 1 on `[5,1,5]` where 5 is
    attainable; task 386 answers NO for `abacaba`, which splits as `ab|acaba`.

The remaining **36 disagreements are not adjudicated** and are listed below. They should
be treated as the least reliable entries in either file:

63, 95, 107, 147, 148, 165, 184, 186, 187, 188, 200, 211, 213, 214, 222, 223, 225, 236,
250, 251, 302, 330, 336, 337, 347, 425, 483, 493, 494, 499, 529, 544, 546, 547, 558, 627,
629, 633 *(task_ids)*

The lesson from the adjudicated sample is that a stated reason from either evaluation can
be confidently wrong in both directions, and that the statement's own sample is the most
reliable tiebreaker.

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
   correct / 318 incorrect.)*

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
| `agent_verdicts.json` | Per-case verdict, confidence, reason, counterexample input, sample-test outcome |
| `agent_verdicts.csv` | Same, flattened for spreadsheets |
| `EVALUATION.md` | This report |
