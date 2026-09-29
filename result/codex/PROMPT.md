# Codex agent prompt

This is the user-prompt template passed to each fresh Codex evaluation session. `{START_ID}` and `{END_ID}` were replaced with that batch's inclusive task-ID range. The universal review rule remained identical for every task.

```text
Fresh independent evaluation batch. Evaluate exactly task IDs {START_ID} through {END_ID} from data/mirror_data.json.

Use this exact universal rule for every record:
"Read the complete description, examples, constraints, and candidate_code. By ordinary static reasoning, decide whether the candidate code satisfies the description for all valid inputs. Check algorithm logic, required input/output, boundary cases, stated constraints, and obvious runtime failures. Mark false only when you can identify a concrete mismatch; otherwise mark true when the implementation reasonably appears correct."

Read every complete record in this range using one or a few simple jq/sed reads. Do not inspect any other files. Do not execute candidate code, make or run tests, build reference solutions, use solvers, use the internet, inspect git/history/prior results, or use specialized per-task workflows. Do not force or target any true/false ratio. Do not default-fill records.

Create results/batch.json using apply_patch. Its object must contain range_start={START_ID}, range_end={END_ID}, and results sorted by task_id. Include exactly IDs {START_ID} through {END_ID} once each. Every result must contain exactly task_id, satisfies_description (boolean), and reason (one short nonempty sentence). A false reason must state the specific concrete mismatch; never use a generic placeholder. A true reason may briefly state that the approach matches. Validate this batch once with jq, then stop.
```
