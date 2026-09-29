# Agent prompt

The exact prompt used for every one of the 645 judgements. It is identical for all
tasks — there is no per-problem or per-case tailoring, and nothing else is sent.

Each request is a single stateless call containing only the system prompt below and one
user message built from one task's `description` and `candidate_code`. No conversation
history, no other task, no tools.

## System prompt

```text
You judge whether a Python program is a correct solution to a programming task.
Judge it as a competitive-programming submission: it must give right answers for all inputs allowed by the stated constraints (not just the example in the statement), print output in the required format, run fast enough for the stated limits, and not crash. If the statement says any valid answer is accepted, any valid answer counts.
This is a quick judgement - do not deliberate at length.
```

## User message

Built per task by substituting the two fields of that task's dataset record:

```text
TASK DESCRIPTION:
{description}

CANDIDATE PROGRAM:
{candidate_code}

Is this program a correct solution to the task?
```

`{description}` is the record's `description` verbatim; `{candidate_code}` is its
`candidate_code` verbatim. Neither is truncated or edited.

## Response format

The reply is constrained by this JSON schema, so the model must return one of the two
labels and cannot answer with prose:

```json
{
  "type": "object",
  "properties": {
    "verdict": {
      "type": "string",
      "enum": [
        "correct",
        "incorrect"
      ]
    }
  },
  "required": [
    "verdict"
  ],
  "additionalProperties": false
}
```

## Decoding settings

| Setting | Value |
|---|---|
| model | `claude-sonnet-5` |
| effort | `low` |
| thinking | disabled |
| max_tokens | 64 |
| tools | none |
| temperature | not set (API default) |

Full run configuration, including usage and isolation properties, is in
[`settings.json`](settings.json); the runner that issued these requests is
[`run_eval.py`](run_eval.py).
