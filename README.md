# MirrorData

MirrorData is a label-free view of the 645-case HoarePrompt experimental
split for blind program-correctness evaluation. Each case exposes its task
identifier, programming-task description, and one candidate Python program.

## Dataset

The dataset is stored in [`data/mirror_data.json`](data/mirror_data.json) as a
JSON array. Every object has exactly three fields:

```json
{
  "task_id": "1919_A",
  "description": "The complete programming-task description...",
  "candidate_code": "The candidate Python program..."
}
```

The file deliberately excludes correctness labels, candidate-specific IDs,
counterexamples, generated outputs, test results, model names, difficulty
metadata, and benchmark scores. Example inputs and outputs that occur inside
the original task statement remain part of `description`.

Load it with Python:

```python
import json
from pathlib import Path

cases = json.loads(Path("data/mirror_data.json").read_text())
for case in cases:
    task_id = case["task_id"]
    description = case["description"]
    candidate_code = case["candidate_code"]
```

## Provenance

MirrorData is derived from the 645-case `CoCoClaNeL_experiments.json` split in
the [HoarePrompt-data repository](https://github.com/msv-lab/HoarePrompt-data).
The transformation is intentionally minimal:

- `task_id` is copied to `task_id`.
- `description` is copied to `description`.
- `generated_code` is copied to `candidate_code`.
- Every other source field is removed.

The order of cases is unchanged from the source split.

## License

The source dataset is distributed under the MIT License. See [LICENSE](LICENSE).
